import os
import re

#检查pull.py运行下载的笔记文件是否有错误
def check_error_mdfile():
    reg = r'\[.*?\]\((.*?note\.youdao\.com.*?)\)'
    p = re.compile(reg)
    note_download_path = './youdaonote'
    notebooknames = os.listdir(note_download_path)
    for notebookname in notebooknames:
        if 'images' in notebookname or 'attachments' in notebookname:
            print(notebookname)
            continue
        notefiles = os.scandir(os.path.join(note_download_path, notebookname))
        for notefile in notefiles:
            notefilename = notefile.name
            if notefile.is_dir():
                continue
            notefilename_lst = notefilename.split('.')
            if len(notefilename_lst) < 2:
                print('存在命名错误笔记本:' + notebookname + '笔记:' + notefilename)
                # 删除无后缀的文件
                # os.remove(os.path.join(note_download_path, notebookname, notefilename))
            elif notefilename.split('.')[-1] == 'md':
                with open(os.path.join(note_download_path, notebookname, notefilename), 'rb') as mdStream:
                    text = mdStream.read().decode('utf-8')
                    urls = p.findall(text)
                if len(urls) > 0:
                    print('存在链接未下载笔记本:' + notebookname + '笔记:' + notefilename)
                    # 将有有道云链接的md note文件移动到其他文件夹
                    os.renames(os.path.join(note_download_path, notebookname, notefilename),
                               os.path.join(note_download_path, notebookname, '需更新链接8', notefilename))
                    os.renames(os.path.join(note_download_path, notebookname, notefilename[:-2] + 'note'),
                               os.path.join(note_download_path, notebookname, '需更新链接8', notefilename[:-2] + 'note'))

#遍历笔记文件，替换图片、附件地址为自己搭建的webdav
def update_link():
    # reg = r'\[.*?\]\((.*?note\.youdao\.com.*?)\)'
    reg = r'\[(.*?)\]\(\.{1,2}/youdaonote-(attachments|images)/(.*?)\)'
    # reg = r'\[.*?\]\((\.\./youdaonote-images/.*?)\)'
    # reg = r'(?<='
    p = re.compile(reg)
    note_download_path = './youdaonote'
    notebooknames = os.listdir(note_download_path)
    for notebookname in notebooknames:
        notefiles = os.scandir(os.path.join(note_download_path, notebookname))
        for notefile in notefiles:
            notefilename = notefile.name
            if not notefile.is_dir():
                notefilename_lst = notefilename.split('.')
                if len(notefilename_lst) >= 2 and notefilename.split('.')[-1] == 'md':
                    with open(os.path.join(note_download_path, notebookname, notefilename), 'rb') as mdStream:
                        content = mdStream.read().decode('utf-8')
                        new_content = p.sub(r'[\1](http://192.168.2.1:16177/joplin/\2/\3)', content)

                    if content != new_content:
                        os.remove(os.path.join(note_download_path, notebookname, notefilename))
                        with open(os.path.join(note_download_path, notebookname, notefilename), 'wb') as mdStream:
                            mdStream.write(new_content.encode('utf-8'))


if __name__ == '__main__':
    # check_error_mdfile()
    # update_link()