import os
import io
import sys
import urllib.parse
import argparse
import requests
from zipfile import ZipFile
from dotenv import Dotenv

def flatten(d):
    return_dict = {}

    for k, v in d.items():
        if isinstance(v, dict):
            for nested_k, nested_v in flatten(v).items():
                return_dict[k + '/' + nested_k] = nested_v

        else:
            return_dict[k] = v

    return return_dict

def select_dict(d, keys):
    return {k: v for k, v in d.items() if k in keys}

class NicoOpendata(object):

    origin = 'https://nico-opendata.jp'

    list_paths = {
        'common': {
            'tag_list': '/distribution/tags/list.txt',
        },
        'seiga': {
            'meta_data': '/distribution/metadata/list.txt',
            'image_data': '/distribution/image-data/list.txt',
            'image_id_list': '/distribution/image-id-list/list.txt',
        },
        'syunga': {
            'meta_data': '/distribution/adult-metadata/list.txt',
            'image_data': '/distribution/adult-image-data/list.txt',
            'image_id_list': '/distribution/adult-image-id-list/list.txt',
        },
    }

    def __init__(self, param_list):
        self.params = param_list
        self.params = urllib.parse.urlencode(self.params)
        self.params = urllib.parse.unquote(self.params)

    def url(self, path):
        return self.origin + path + '?' + self.params

    def get_file_list(self, path):
        response = requests.get(self.url(path))
        file_paths = response.text.split('\n')
        file_paths = [p for p in file_paths if p]
        return file_paths

    def extension(self, path):
        return os.path.splitext(path)[1][1:]

    def unzip(self, zipped_data, path):
        with ZipFile(io.BytesIO(zipped_data)) as z:
            z.extractall(path)

    def get_file(self, path, binary=False):
        response = requests.get(self.url(path))

        if binary:
            return response.content
        else:
            return response.text

    def download_file(self, target, output_dir='./', extract=True):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_dir = os.path.abspath(output_dir)

        for path in self.get_file_list(target):
            filename = os.path.basename(path)

            if extract and self.extension(path) == 'zip':
                data = self.get_file(path, binary=True)
                self.unzip(data, output_dir)
            else:
                data = self.get_file(path)
                with open('{}/{}'.format(output_dir, filename), 'w') as f:
                    f.write(data)

            print('Downloaded: .{}'.format(path))



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-t', '--target', nargs='*')
    parser.add_argument('-o', '--output', default='.')

    parser_unzip = parser.add_mutually_exclusive_group()
    parser_unzip.add_argument('--unzip', '--extract', dest='unzip', action='store_true')
    parser_unzip.add_argument('--no-unzip', '--no-extract', dest='unzip', action='store_false')
    parser.set_defaults(unzip=True)

    args = parser.parse_args()

    dotenv = Dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    nico = NicoOpendata(dotenv)

    list_paths = flatten(nico.list_paths)
    output = os.path.abspath(args.output)

    if args.all:
        paths = list_paths

    if not args.all and args.target:
        paths = select_dict(list_paths, args.target)

    for key, target in paths.items():
        nico.download_file(target, output_dir='{}/{}'.format(output, key), extract=args.unzip)
