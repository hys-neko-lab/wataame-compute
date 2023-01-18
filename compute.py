from api import compute_pb2
from api import compute_pb2_grpc
import libvirt
import string
import os

class Compute(compute_pb2_grpc.ComputeServicer):
    def __init__(self):
        self.conn = libvirt.open('qemu:///system')

    def startVM(self, request, context):
        if self.conn == None:
            message = "conn failed."
            return compute_pb2.StartReply(message=message)

        dom = self.conn.lookupByUUIDString(request.uuid)
        if dom == None:
            message = "find domain failed."
            return compute_pb2.StartReply(message=message)

        if dom.create() != 0:
            message = "create domain failed."
            return compute_pb2.StartReply(message=message)

        message = "UUID:" + request.uuid + " started."
        return compute_pb2.StartReply(message=message)

    def shutdownVM(self, request, context):
        if self.conn == None:
            message = "conn failed."
            return compute_pb2.ShutdownReply(message=message)

        dom = self.conn.lookupByUUIDString(request.uuid)
        if dom == None:
            message = "find domain failed."
            return compute_pb2.ShutdownReply(message=message)

        if dom.shutdown() != 0:
            message = "shutdown domain failed."
            return compute_pb2.ShutdownReply(message=message)

        message = "UUID:" + request.uuid + " shutdown."
        return compute_pb2.ShutdownReply(message=message)


    def destroyVM(self, request, context):
        if self.conn == None:
            message = "conn failed."
            return compute_pb2.DestroyReply(message=message)

        dom = self.conn.lookupByUUIDString(request.uuid)
        if dom == None:
            message = "find domain failed."
            return compute_pb2.DestroyReply(message=message)

        if dom.destroy() != 0:
            message = "destroy domain failed."
            return compute_pb2.DestroyReply(message=message)

        message = "UUID:" + request.uuid + " destroy."
        return compute_pb2.DestroyReply(message=message)

    def deleteVM(self, request, context):
        if self.conn == None:
            message = "conn failed."
            return compute_pb2.DeleteReply(message=message)

        dom = self.conn.lookupByUUIDString(request.uuid)
        if dom == None:
            message = "find domain failed."
            return compute_pb2.DeleteReply(message=message)

        if dom.undefine() != 0:
            message = "delete domain failed."
            return compute_pb2.DeleteReply(message=message)

        message = "UUID:" + request.uuid + " deleted."
        return compute_pb2.DeleteReply(message=message)

    def createVM(self, request, context):
        if self.conn == None:
            message = "conn failed."
            return compute_pb2.CreateReply(message=message)

        # 仮想マシンインストールテンプレートの書き換え
        with open('templates/install.xml') as f:
            t = string.Template(f.read())
        xmlcreate = t.substitute(
            name=request.name,
            uuid=request.uuid,
            vmlinuzpath=os.path.abspath("data/vmlinuz"),
            initrdpath=os.path.abspath("data/initrd"),
            imgpath=request.imgpath,
            isopath=os.path.abspath("data/ubuntu-20.04.5-live-server-amd64.iso"),
            mac=request.mac
        )
        print(xmlcreate)

        # 仮想マシン定義テンプレートの書き換え
        with open('templates/define.xml') as f:
            t = string.Template(f.read())
        xmldefine = t.substitute(
            name=request.name,
            uuid=request.uuid,
            imgpath=request.imgpath,
            network=request.network,
            mac=request.mac
        )
        print(xmldefine)

        # user-dataの書き換え
        with open('templates/user-data') as f:
            t = string.Template(f.read())
        userdata = t.substitute(
            hostname=request.hostname,
            password_hash=request.password_hash,
            username=request.username,
            pubkey=request.pubkey
        )
        print(userdata)

        # userdataをcloud-initの簡易webサーバディレクトリに一時保存
        tempdir='www/{}'.format(request.uuid)
        os.makedirs(tempdir, exist_ok=True)
        with open(os.path.join(tempdir, "user-data"),'w') as ud:
            print(userdata, file=ud)
        with open(os.path.join(tempdir, "meta-data"),'w') as md:
            print('', file=md)

        # 仮想マシンを定義し作成を開始
        dom = self.conn.defineXMLFlags(xmldefine, 0)
        if dom == None:
            message = "define domain failed"
            return compute_pb2.CreateReply(message=message)
        if self.conn.createXML(xmlcreate, 0) == None:
            message = "create domain failed."
            return compute_pb2.CreateReply(message=message)
        print("create VM succeeded")
        
        message = "UUID:" + request.uuid + " created."
        return compute_pb2.CreateReply(message=message)

    def getStatus(self, request, context):
        if self.conn == None:
            message = "conn failed."
            return compute_pb2.StatusReply(message=message)
        
        dom = self.conn.lookupByUUIDString(request.uuid)
        if dom == None:
            message = "find domain failed."
            return compute_pb2.StatusReply(message=message)
        
        # 仮想マシンの状態を取得しリプライメッセージをセット
        state, reason = dom.state()
        if state == libvirt.VIR_DOMAIN_NOSTATE:
            message = "NOSTATE"
        elif state == libvirt.VIR_DOMAIN_RUNNING:
            message = "RUNNING"
        elif state == libvirt.VIR_DOMAIN_BLOCKED:
            message = "BLOCKED"
        elif state == libvirt.VIR_DOMAIN_PAUSED:
            message = "PAUSED"
        elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
            message = "SHUTDOWN"
        elif state == libvirt.VIR_DOMAIN_SHUTOFF:
            message = "SHUTOFF"
        elif state == libvirt.VIR_DOMAIN_CRASHED:
            message = "CRASHED"
        elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
            message = "SUSPENDED"
        else:
            message = "UNKNOWN"

        return compute_pb2.StatusReply(message=message)

    def getIP(self, request, context):
        if self.conn == None:
            message = "conn failed."
            return compute_pb2.IPReply(message=message)
        
        dom = self.conn.lookupByUUIDString(request.uuid)
        if dom == None:
            message = "find domain failed."
            return compute_pb2.IPReply(message=message)
        
        # 仮想マシン内のqemu-guest-agentからIPの情報をもらう
        try:
            ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        except:
            message = "get address failed."
            return compute_pb2.IPReply(message=message)
        
        for (name, val) in ifaces.items():
            if val['addrs']:
                for ipaddr in val['addrs']:
                    if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                        if ipaddr['addr'] != '127.0.0.1':
                            message = ipaddr['addr']
        return compute_pb2.IPReply(message=message)

        