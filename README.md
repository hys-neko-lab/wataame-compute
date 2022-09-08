First, download ubuntu-20.04.5-live-server-amd64.iso from http://releases.ubuntu.com/20.04/

Then run following commands.

```sh
$ cd wataame-compute
$ mkdir data
$ cd data
$ mv ~/Downloads/ubuntu-20.04.5-live-server-amd64.iso ./
$ sudo mount -r ubuntu-20.04.5-live-server-amd64.iso /mnt
$ cp /mnt/casper/initrd ./
$ cp /mnt/casper/vmlinuz ./
$ sudo umount /mnt
```