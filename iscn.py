# -*- coding: utf-8 -*-
# check if the IP is in the assigned IP blocks
import argparse
import logging
import requests
import sys


def init_logging():
    formatting = '%(asctime)-15s %(levelname)-8s [ %(filename)s:%(lineno)d ~ %(processName)s(%(process)d) ] %(message)s'
    logging.basicConfig(format=formatting)
    logging.getLogger().setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apnic_url', '-u', type=str, default='http://ftp.apnic.net/stats/apnic/delegated-apnic-latest', help='APNIC URL')
    parser.add_argument('--apnic_assigned_file', '-f', type=str, default='assigned.txt', help='APNIC assigned file')
    parser.add_argument('--input_file', '-i', type=str, default='input.txt', help='input file')
    parser.add_argument('--stdin', '-s', action=argparse.BooleanOptionalAction, help='read from stdin')
    args = parser.parse_args()
    return args


# assigned ipv4 status by apnic
# http://ftp.apnic.net/stats/apnic/delegated-apnic-latest
def load_from_url(url: str):
    return requests.get(url).text


def load_from_file(file: str):
    with open(file, 'r') as f:
        return f.read()


def add_ip_block(dict_target: dict, ip_start: str, ip_end: str):
    blocks_start = ip_start.split('.')
    blocks_end = ip_end.split('.')
    if len(blocks_start) == 4 and len(blocks_end) == 4:
        if blocks_start[0] == blocks_end[0]:
            if not blocks_start[0] in dict_target:
                dict_target[blocks_start[0]] = {}
            if blocks_start[1] == blocks_end[1]:
                if not blocks_start[1] in dict_target[blocks_start[0]]:
                    dict_target[blocks_start[0]][blocks_start[1]] = {}
                if blocks_start[2] == blocks_end[2]:
                    if not blocks_start[2] in dict_target[blocks_start[0]][blocks_start[1]]:
                        dict_target[blocks_start[0]][blocks_start[1]][blocks_start[2]] = 1
                else:
                    for i in range(int(blocks_start[2]), int(blocks_end[2]) + 1):
                        if not str(i) in dict_target[blocks_start[0]][blocks_start[1]]:
                            dict_target[blocks_start[0]][blocks_start[1]][str(i)] = 1
            else:
                for i in range(int(blocks_start[1]), int(blocks_end[1]) + 1):
                    if not str(i) in dict_target[blocks_start[0]]:
                        dict_target[blocks_start[0]][str(i)] = {}
                    for j in range(256):
                        if not str(j) in dict_target[blocks_start[0]][str(i)]:
                            dict_target[blocks_start[0]][str(i)][str(j)] = 1
        else:
            for i in range(int(blocks_start[0]), int(blocks_end[0]) + 1):
                if not str(i) in dict_target:
                    dict_target[str(i)] = {}
                    for j in range(256):
                        if not str(j) in dict_target[str(i)]:
                            dict_target[str(i)][str(j)] = {}
                        for k in range(256):
                            dict_target[str(i)][str(j)][str(k)] = 1


def load_assigned_ip_blocks(target_dict: dict, text: str):
    target_dict.clear()
    for line in text.split('\n'):
        items = line.strip().split('|')
        if len(items) == 7:
            country = items[1]
            ip_type = items[2]
            ip_start = items[3]
            size = int(items[4])
            status = items[6]
            if country == 'CN' and ip_type == 'ipv4' and status == 'allocated':
                ip_blocks = ip_start.split('.')
                if size >= 2**25:
                    append = int(size / (2**24))
                    ip_end_b0 = str(int(ip_blocks[0]) + append - 1)
                    ip_end = '.'.join([ip_end_b0, '255', '255', '255'])
                    add_ip_block(target_dict, ip_start, ip_end)
                elif size >= 2**17:
                    append = int(size / (2**16))
                    ip_end_b1 = str(int(ip_blocks[1]) + append - 1)
                    ip_end = '.'.join([ip_blocks[0], ip_end_b1, '255', '255'])
                    add_ip_block(target_dict, ip_start, ip_end)
                elif size >= 2**9:
                    append = int(size / (2**8))
                    ip_end_b2 = str(int(ip_blocks[2]) + append - 1)
                    ip_end = '.'.join([ip_blocks[0], ip_blocks[1], ip_end_b2, '255'])
                    add_ip_block(target_dict, ip_start, ip_end)
                else:
                    append = size
                    ip_end_b3 = str(int(ip_blocks[3]) + append - 1)
                    ip_end = '.'.join([ip_blocks[0], ip_blocks[1], ip_blocks[2], ip_end_b3])
                    add_ip_block(target_dict, ip_start, ip_end)


def main():
    init_logging()
    args = parse_args()
    dict_target = {}
    if args.apnic_url is not None and args.apnic_url != '':
        logging.info(f'Load assigned IP blocks from {args.apnic_url}')
        load_assigned_ip_blocks(dict_target, load_from_url(args.apnic_url))
    elif args.apnic_assigned_file is not None and args.apnic_assigned_file != '':
        logging.info(f'Load assigned IP blocks from {args.apnic_assigned_file}')
        load_assigned_ip_blocks(dict_target, load_from_file(args.apnic_assigned_file))
    else:
        logging.error('No assigned IP blocks loaded')
    logging.info(f'Assigned IP blocks: {len(dict_target)}')
    if args.stdin:
        logging.info('Parsing dig result from stdin')
        for line in sys.stdin:
            items = line.strip().split('\t')
            if len(items) < 3:
                continue
            tp = items[-2]
            ip = items[-1]
            if tp == 'A':
                blocks = ip.split('.')
                if len(blocks) == 4:
                    if blocks[0] in dict_target and blocks[1] in dict_target[blocks[0]] and blocks[2] in dict_target[blocks[0]][blocks[1]]:
                        print(line.strip())
    else:
        logging.info(f'Parsing dig result from {args.input_file}')
        text = load_from_file(args.input_file)
        for line in text.split('\n'):
            items = line.strip().split('\t')
            if len(items) < 3:
                continue
            tp = items[-2]
            ip = items[-1]
            if tp == 'A':
                blocks = ip.split('.')
                if len(blocks) == 4:
                    if blocks[0] in dict_target and blocks[1] in dict_target[blocks[0]] and blocks[2] in dict_target[blocks[0]][blocks[1]]:
                        print(line.strip())


if __name__ == '__main__':
    main()
