import boto3
import csv
import io
"""
Classes to support reading unpacked bag file content from s3 (with a view to
sending it to OpenSearch).
"""


class BagError(Exception):
    """
    To report bag read errors.
    """


class BagFileMapper:
    """
    Assign each file name from an arbitrary file list to a property. Top-level
    bag file names (such as `bag-info.txt`) go to respective class-level
    `str` properties. Bag file names in sub folders go to a list.

    On error raises BagReaderError.
    """
    BAG_BAG_INFO = 'bag-info.txt'
    BAG_BAGIT = 'bagit.txt'
    BAG_FILE_AV = 'file-av.csv'
    BAG_FILE_FFID_CSV = 'file-ffid.csv'
    BAG_FILE_METADATA = 'file-metadata.csv'
    BAG_MANIFEST_SHA256 = 'manifest-sha256.txt'
    BAG_TAGMANIFEST_SHA256 = 'tagmanifest-sha256.txt'

    # Explicitly declare properties set by __init__ method
    bag_sub_file_list = None
    bag_info_txt = None
    bagit_txt = None
    file_av_csv = None
    file_ffid_csv = None
    file_metadata_csv = None
    manifest_sha_256_txt = None
    tagmanifest_sha_256_txt = None

    def __init__(
            self,
            file_list: list,
            path_prefix: str = '',
            only_expected_root_files: bool = False
    ):
        """
        Map list of bag files to respective class properties.

        :param file_list: List of bag file paths
        :param path_prefix: Optional path prefix to bag root
        :param only_expected_root_files: Default False value permits skipping
        of unexpected files exist in bag root; set True to raise error instead
        """
        print(f'__init__: file_list={file_list}')
        print(f'__init__: path_prefix={path_prefix}')
        self.bag_sub_file_list = []

        for bag_file_full_path in file_list:
            print(f'__init__: bag_file_full_path={bag_file_full_path}')
            bag_file = str(bag_file_full_path).removeprefix(path_prefix)
            if bag_file == self.BAG_BAG_INFO:
                self.bag_info_txt = bag_file_full_path
            if bag_file == self.BAG_BAGIT:
                self.bagit_txt = bag_file_full_path
            if bag_file == self.BAG_FILE_AV:
                self.file_av_csv = bag_file_full_path
            if bag_file == self.BAG_FILE_FFID_CSV:
                self.file_ffid_csv = bag_file_full_path
            if bag_file == self.BAG_FILE_METADATA:
                self.file_metadata_csv = bag_file_full_path
            if bag_file == self.BAG_MANIFEST_SHA256:
                self.manifest_sha_256_txt = bag_file_full_path
            if bag_file == self.BAG_TAGMANIFEST_SHA256:
                self.tagmanifest_sha_256_txt = bag_file_full_path
            elif '/' in bag_file:
                self.bag_sub_file_list.append(bag_file_full_path)
            else:
                if only_expected_root_files:
                    raise BagError(
                        f'unexpected file in bag root: {bag_file_full_path}'
                    )

        if self.bag_info_txt is None:
            raise BagError(f'No input file for "{self.BAG_BAG_INFO}"')

        print(f'BagFileMapper: self.bag_sub_file_list={self.bag_sub_file_list}')


class S3BagReader(BagFileMapper):
    def __init__(
            self,
            s3_bucket: str,
            file_list: list,
            path_prefix: str = '',
            only_expected_root_files: bool = False,
            s3_api=None
    ):
        """
        Provides methods to read bag files unpacked on s3.

        :param s3_bucket: Name of s3 bucket holding unpacked files.
        :param file_list: List of bag file paths
        :param path_prefix: Optional path prefix to bag root
        :param only_expected_root_files: Default False value permits skipping
        of unexpected files exist in bag root; set True to raise error instead
        :param s3_api: Optionally pass an existing boto3.client('s3') instance
        """
        super().__init__(file_list=file_list, path_prefix=path_prefix)
        self.s3_bucket = s3_bucket
        self.only_expected_root_files = only_expected_root_files
        if s3_api:
            print(f'Using externally provided s3_api instance')
            self.s3_api = s3_api
        else:
            print(f'Creating internal s3_api instance')
            self.s3_api = boto3.client('s3')

        print(f'S3BagReader: self.bag_sub_file_list={self.bag_sub_file_list}')

    @staticmethod
    def get_property_file_as_dict(s3_object) -> dict:
        """
        Return dictionary representation of a property file.
        :param s3_object: S3 API object instance (AWS boto3 s3 API get_object)
        :return: Dictionary of property file key/value pairs
        """
        output = {}
        lines = s3_object['Body'].read().decode('utf-8').splitlines()
        for line in lines:
            line_items = line.strip().split(':', 1)
            output[line_items[0].strip()] = line_items[1].strip()
        return output

    @staticmethod
    def get_checksum_file_as_list(s3_object) -> list:
        """
        Return list representation of checksum file entries.
        :param s3_object: S3 API object instance (AWS boto3 s3 API get_object)
        :return: List of checksum file entries pairs (file -> checksum)
        """
        output = []
        lines = s3_object['Body'].read().decode('utf-8').splitlines()
        for line in lines:
            line_items = line.strip().replace('\t', ' ').split(' ', 1)
            line_dict = {
                'object': line_items[1].strip(),
                'checksum': line_items[0].strip()
            }
            output.append(line_dict)
        return output

    @staticmethod
    def get_csv_file_as_list(s3_object) -> list:
        """
        Return dictionary representation of a csv file.
        :param s3_object: S3 API object instance (AWS boto3 s3 API get_object)
        :return: List of dictionaries of csv file records
        """
        output = []
        lines = s3_object['Body'].read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(lines)
        for line in csv_reader:
            # Set empty strings to None (so null later in OpenSearch JSON)
            for k, v in line.items():
                if v == '':
                    line[k] = None

            output.append(line)
        return output

    def get_bag_info_txt_as_dict(self) -> dict:
        s3_object = self.s3_api.get_object(Bucket=self.s3_bucket, Key=self.bag_info_txt)
        data = self.get_property_file_as_dict(s3_object)
        return {
            self.BAG_BAG_INFO: data
        }

    def get_bagit_txt_as_dict(self) -> dict:
        s3_object = self.s3_api.get_object(Bucket=self.s3_bucket, Key=self.bagit_txt)
        data = self.get_property_file_as_dict(s3_object)
        return {
            self.BAG_BAGIT: data
        }

    def get_file_av_csv_as_dict(self) -> dict:
        if self.file_av_csv:
            s3_object = self.s3_api.get_object(Bucket=self.s3_bucket, Key=self.file_av_csv)
            data = self.get_csv_file_as_list(s3_object)
            return {
                self.BAG_FILE_AV: data
            }
        else:
            print(f'get_file_av_csv_as_dict: file not found')
            return {}

    def get_file_ffid_csv_as_dict(self) -> dict:
        if self.file_ffid_csv:
            s3_object = self.s3_api.get_object(Bucket=self.s3_bucket, Key=self.file_ffid_csv)
            data = self.get_csv_file_as_list(s3_object)
            return {
                self.BAG_FILE_FFID_CSV: data
            }
        else:
            print(f'get_file_ffid_csv_as_dict: file not found')
            return {}

    def get_file_metadata_csv_as_dict(self) -> dict:
        if self.file_metadata_csv:
            s3_object = self.s3_api.get_object(Bucket=self.s3_bucket, Key=self.file_metadata_csv)
            data = self.get_csv_file_as_list(s3_object)
            return {
                self.BAG_FILE_METADATA: data
            }
        else:
            print(f'get_file_metadata_csv_as_dict: file not found')
            return {}

    def get_manifest_sha256_as_dict(self) -> dict:
        s3_object = self.s3_api.get_object(Bucket=self.s3_bucket, Key=self.manifest_sha_256_txt)
        data = self.get_checksum_file_as_list(s3_object)
        return {
            self.BAG_MANIFEST_SHA256: data
        }

    def get_tagmanifest_sha256_as_dict(self) -> dict:
        s3_object = self.s3_api.get_object(Bucket=self.s3_bucket, Key=self.tagmanifest_sha_256_txt)
        data = self.get_checksum_file_as_list(s3_object)
        return {
            self.BAG_TAGMANIFEST_SHA256: data
        }

    def get_sub_files_dict(self) -> dict:
        """
        Returns sub-file content as:
            {
                'bag_sub_files': [
                    {
                        'object': '',
                        'data': ''
                    }
                ]
            }
        """
        text_files = ['.txt', '.csv']
        file_list = []
        print(f'self.bag_sub_file_list:\n{self.bag_sub_file_list}')
        for sub_file in self.bag_sub_file_list:
            if str(sub_file)[-4:] in text_files:
                print(f'Loading text file: {sub_file}')
                reader = io.BytesIO()
                self.s3_api.download_fileobj(
                    Bucket=self.s3_bucket,
                    Key=sub_file,
                    Fileobj=reader
                )

                file_list.append(
                    {
                        'object': sub_file,
                        'data': reader.getvalue().decode()
                    }
                )
            else:
                print(f'Skipping file "{sub_file}"; not in "{text_files}"')

        data = {
            'bag_sub_files': file_list
        }

        return data
