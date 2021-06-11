The script is for partitions in CPC life-cycle testing. Include partition create/start/stop/delete, add vNic, attach FCP storage group, set boot option, etc.

Now the script deployed in YJ-rhel7-vm (9.112.234.95) server, under /root/git/longevity/    // obsolete!
Now the script deployed in liwbj (9.110.179.218) server, under directory /home/yj/git/longevity/

And there have 5 cron jobs run the scripts:     // obsoleted!
Only partition life-cycle now running~

# YJ for T90 longivity test located in /root/git/longevity/
0 * * * * cd /root/git/longevity/src/ && /usr/bin/python partitionLifecycle.py lc1
0 * * * * cd /root/git/longevity/src/ && /usr/bin/python changePartitionStatus.py ubut2
40 23 * * * cd /root/git/longevity/src/ && /usr/bin/python checkStorageGroupsStatus.py all
45 23 * * * cd /root/git/longevity/src/ && /usr/bin/python checkPartitionStatus.py t90parts
50 23 * * * cd /root/git/longevity/src/ && /usr/bin/python statistic.py
