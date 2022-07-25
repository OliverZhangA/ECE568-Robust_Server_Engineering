#sudo systemd-run --scope -p CPUQuota=30% ./serv
#
#or
#sudo taskset -c 0 ./serv
u=postgres # do not set this to root!
c=0-3
for p in $(pgrep -u $u)
  do
    sudo taskset -cp $c $p
done


# #first run: taskset -c c ./serv
# #!/bin/bash
# c=0
# postmaster_pid=$(pidof postgres | xargs -n1 | sort | head -n1)
# sudo taskset -pc $c $postmaster_pid
# sudo pidof postgres -o $postmaster_pid | xargs -n1 taskset -pc $c