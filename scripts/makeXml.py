# -*- coding: utf-8 -*-
import os
import codecs
import zipfile
import ConfigParser
import StringIO
import time

XML_TEMPLATE = '''
    <pyqgis_plugin name="{plugin_name}" version="{version}" plugin_id="{id}">
        <description><![CDATA[{description}]]></description>
        <about><![CDATA[{about}]]></about>
        <version><![CDATA[{version}]]></version>
        <trusted>False</trusted>
        <qgis_minimum_version>{qgis_minimum_version}</qgis_minimum_version>
        <qgis_maximum_version>{qgis_maximum_version}</qgis_maximum_version>
        <homepage><![CDATA[{homepage}]]></homepage>
        <file_name>{folder_name}.zip</file_name>
        <icon>https://kr-ngii.github.io/icons/{folder_name}/icon.png</icon>
        <author_name><![CDATA[{author_name}]]></author_name>
        <download_url>https://kr-ngii.github.io/download/{crr_zip_file}</download_url>
        <create_date>{create_date}</create_date>
        <update_date>{update_date}</update_date>
        <experimental>False</experimental>
        <deprecated>False</deprecated>
        <tracker><![CDATA[{tracker}]]></tracker>
        <repository><![CDATA[{repository}]]></repository>
        <tags><![CDATA[{tags}]]></tags>
        <external_dependencies></external_dependencies>
        <server>False</server>
    </pyqgis_plugin>
'''


def main():
    src_dir = "../download"
    out_xml_file_path = os.path.join("../plugins.xml")
    file_list = [os.path.join(src_dir, file_name) for file_name in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, file_name)) and (os.path.splitext(file_name)[1]).lower() == ".zip"]

    try:
        with codecs.open(out_xml_file_path, "w", "utf-8") as out_xml:
            out_xml.write("<?xml version = '1.0' encoding = 'UTF-8'?>\n")
            out_xml.write('<plugins>')
            plugin_id = 100000
            for zip_file_path in file_list:
                with zipfile.ZipFile(zip_file_path) as zip_file:
                    # ROOT 폴더만 추출
                    folders = [folder_name[:-1] for folder_name in zip_file.namelist() if folder_name.endswith('/') and folder_name.count("/") == 1]
                    if len(folders) != 1:
                        raise Exception(u"ZIP 파일의 루트에 플러그인 폴더 외의 폴더가 있음")
                    folder_name = folders[0]
                    print folder_name

                    # metadata.txt
                    metadata_txt = zip_file.read("{}/metadata.txt".format(folder_name))
                    print metadata_txt

                    metadata = ConfigParser.ConfigParser()
                    metadata.readfp(StringIO.StringIO(metadata_txt))

                    icon_file = metadata.get("general", "icon")
                    src_icon = zip_file.read("{}/{}".format(folder_name, icon_file))

                    icon_folder = os.path.join("../icons/", folder_name)
                    if not os.path.exists(icon_folder):
                        os.makedirs(icon_folder)

                    with open(os.path.join(icon_folder, icon_file), "wb") as out_icon_file:
                        out_icon_file.write(src_icon)

                    xml = XML_TEMPLATE.format(
                        folder_name = folder_name,
                        id = plugin_id,
                        plugin_name = metadata.get("general", "name"),
                        version = metadata.get("general", "version"),
                        description = metadata.get("general", "description"),
                        about = metadata.get("general", "about"),
                        qgis_minimum_version = metadata.get("general", "qgisMinimumVersion"),
                        qgis_maximum_version = "2.99",
                        homepage = metadata.get("general", "homepage"),
                        file_name = folder_name,
                        author_name = metadata.get("general", "author"),
                        crr_zip_file = os.path.basename(zip_file_path),
                        create_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(os.path.getctime(zip_file_path))),
                        update_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(os.path.getmtime(zip_file_path))),
                        tracker = metadata.get("general", "tracker"),
                        repository = metadata.get("general", "repository"),
                        tags = metadata.get("general", "tags")
                    )

                    print xml
                    out_xml.write(xml.decode("utf-8"))
                    plugin_id += 1

            out_xml.write('</plugins>\n')
    except Exception as e:
        print "ERROR: ",
        print (e)

if __name__ == "__main__": main()
