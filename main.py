from cterasdk import *
import logging

def main():
    logging.getLogger().level = logging.INFO
    #admin = ServicesPortal('corp.gfs.ctera.me', port=5000)
    #admin = ServicesPortal('corp.gfs.ctera.me')
    #admin = GlobalAdmin('global.gfs.ctera.me')
    #admin = GlobalAdmin('52.201.75.180')
    #edge = Edge(base='https://corp.gfs.ctera.me/devices/edge-filer-one/')
    with Edge('172.54.3.149') as edge:
        try:
            cterasdk.settings.downloads.location = '~/Desktop'
            edge.login('admin', 'password1!')
            #edge.power.reboot(wait=True)
            #edge.files.download('smb-project-nexus/nist/a/CTERA Enterprise 2022_Intro_External.pptx')
            #edge.files.download_as_zip('smb-project-nexus', 'nist/Saimon Michelson.pdf')
            #edge.files.delete('smb-project-nexus/nist/Saimon Michelson.pdf')
            #edge.files.makedirs('smb-project-nexus/nist/a')
            #edge.files.copy('smb-project-nexus/nist/CTERA Enterprise 2022_Intro_External.pptx', destination='smb-project-nexus/nist/a')
            #edge.files.move('smb-project-nexus/nist/CTERA Enterprise 2022_Intro_External.pptx', destination='smb-project-nexus/nist/a')
            #edge.files.upload(r'c:/users/saimon/Downloads/smb.conf.txt', 'smb-project-nexus/nist')
            #edge.config.import_config(r'c:/users/saimon/Downloads/edge-filer-one.xml')
            #edge.firmware.upgrade(r'c:/users/saimon/Downloads/ctera-firmware-7.5.2820.25.firm')
            #edge.config.export()
            #edge.support.get_support_report()
            #edge.services.connect('corp.gfs.ctera.me', 'saimon_admin', 'Ct#ra321')
            #edge.logout()
            #admin.login('saimon_admin', 'Ct#ra321')
            #admin.login('saimon@ctera.com', 'password1!')
            #admin.backups.device_config('edge-filer-one')
            #admin.files.download('My Files/test.txt')
            #admin.files.download_as_zip('My Files', ['smb.conf.txt'])
            #admin.files.upload(r'c:/users/saimon/Downloads/smb.conf.txt', 'My Files')
            #admin.ssl.import_from_zip(r'c:/users/saimon/Downloads/certificate.zip')
            #admin.logout()
        except CTERAException as error:
            print(error)
    #admin.generic.shutdown()


if __name__ == '__main__':
    main()

