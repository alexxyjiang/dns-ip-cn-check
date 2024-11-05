# dns-ip-cn-check
python script to check whether a domain belongs to china

## usage

```shell
# generate dig result
for line in `cat top2k_domains`; do dig ${line} | ag "^${line}" >> dns_result; done;

# check whether the ip belongs to china, assigned list from apnic latest url, dns result from stdin
cat dns_result | python iscn.py -s > dns_result_cn

# or check whether the ip belongs to china, assigned list from file assigned.txt, dns result from file dns_result
python iscn.py -u '' -f assigned.txt -i dns_result
```
