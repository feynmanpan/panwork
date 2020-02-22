# -*- coding: utf-8 -*
'''
############################
editor: Feynman
python: 3.7.2
history:
    2019-03-13 v1.0   處理標準輸入
    2019-03-14 v1.1   utf8,isnull,dsmark,noattr 測試OK，增加計時
    2019-03-15 v1.2   改用Thread處理每個檔案，refresh,displayat,close,nohelp,clui 測試OK
    2019-03-16 v1.3   4gl,per,4fd,link 測試OK，unicode解碼問題檔案列出及notepad直接開
    2019-03-17 v1.4   pyinstaller打包exe 測試OK
    2019-03-18 v1.5   有些big5解碼問題ignore，否則notepad++會把非法字元轉問號?
    2019-03-19 v1.6   取消'0xe5'
    2019-03-30 v1.7   處理l_za05
    2019-04-01 v1.8   處理temp table內的char放大
    2019-07-25 v1.9   處理GUI with tkinter

Usage：
    █ 1.終端機執行 python XXX.py

    █ 2.依序輸入螢幕要求的資訊：
        --- genero洗檔 with python ---

        (1)輸入來源目錄絕對路徑 [ex: C:\path\...\4gl]:D:\PanWork\python\4gl
        (2)選擇檔案類型 1.4gl 2.per 3.4fd 4.link [ex: 1]:1
        (3)處理方法共有 utf8,noremark
           (utf8強制執行)
           只輸入以逗號分隔的所需處理方法，或Enter全部執行 [ex: utf8,noattr]:

    █ 3.螢幕顯示處理過程及輸出目錄
    ====================== START =============================
    開始處理: asfi300.4gl
    開始處理: hun.4gl
    ...
    開始處理: huni100.4gl
    開始處理: huni101.4gl
    ====================== END =============================
    輸出目錄:  D:/PanWork/python/4gl_py3_utf8_refresh_displayat_isnull_noattr_close_nohelp_dsmark_clui
    共處理 119 個檔案
    共耗時 6.567 秒
    ------------- WARN -------------
    axmt920_exxxxx.per
    axmu006_e.per
    axx.per
    axxx.per
    axmq600xx.per: 無處理
    axmq600x.per: 無處理
    ------------- WARN -------------
    {'0xff', '0xfe', '0xb2', '0xbb', '0xa1'}
    1.以上 37 個原始檔有以上非法字元的解碼問題
    2.註明<無處理>者，輸出檔僅告知UnicodeDecodeError
      其餘則忽略解碼報錯，大部分可轉utf8成功，請留意輸出檔案是否OK
    3.注意: 以NotePad++開啟問題原始檔時，非法字元可能會以問號 ? 呈現
      手動轉utf8後，? 仍會保留

    <請按Enter結束洗檔，或按 y 以Notepad++開啟以上解碼問題原始檔>:y

    █ 4.clui處理範例: asfi300.4gl處理cl_ui_init
    ======================== before ========================
    IF g_lang = '0' THEN
       OPEN WINDOW i300_w AT 3,3
            WITH FORM "asf/frm/asfi300" ATTRIBUTE(BORDER,CYAN)
    ELSE
       OPEN WINDOW i300_w AT 3,3
            WITH FORM "asf/frm/asfi300_e" ATTRIBUTE(BORDER,CYAN)
    END IF

    ======================== after ========================
    ##acerpy_clui_inglang_openwindow_2019-03-16
    {
        IF g_lang = '0' THEN
           OPEN    WINDOW i300_w AT 3,3
                WITH FORM "asf/frm/asfi300" ##acerpy_noattr_2019-03-16 ATTRIBUTE(BORDER,CYAN)
        ELSE
           OPEN    WINDOW i300_w AT 3,3
                WITH FORM "asf/frm/asfi300_e" ##acerpy_noattr_2019-03-16 ATTRIBUTE(BORDER,CYAN)
        END IF
    }
    OPEN    WINDOW i300_w AT 3,3
                WITH FORM "asf/frm/asfi300" ##acerpy_noattr_2019-03-16 ATTRIBUTE(BORDER,CYAN)
    CALL cl_ui_init()
    ##clui_over

    █ 5.isnull處理範例: asfr100.4gl處理g_bgjob
    ======================== before ========================
    IF g_bgjob = ' ' OR g_bgjob = 'N'        # If background job sw is off
        THEN CALL r100_tm()                # Input print condition
        ELSE
            CALL asfr100()            # Read data and create out-file
    END IF

    ======================== after ========================
    ##acerpy_isnull_2019-03-16
    ##   IF g_bgjob = ' ' OR g_bgjob = 'N'        # If background job sw is off
    IF cl_null(g_bgjob) OR g_bgjob = 'N'
        THEN CALL r100_tm()                # Input print condition
        ELSE
            CALL asfr100()            # Read data and create out-file
    END IF
############################
'''

# import
import sys, os, glob, re
from datetime import date
import subprocess
from time import sleep, time
from threading import Thread
import tkinter as tk
import tkinter.messagebox


# helper function
def check_slash(pathstr):
    pathstr = pathstr.replace('\\', '/').strip().strip('/')
    return pathstr


def mytoday():
    return str(date.today())


def checkthen(m):
    '''then可能跟if同行或否'''
    tmpstr = m.group()
    head = m.group(1)
    g_bgjob_g_bookno = m.group(2)
    find = '(.+)then(.*)'
    pattern = re.compile(find, flags=re.I)
    m2 = pattern.search(tmpstr)
    #
    then = " THEN" + m2.group(2) if m2 else ""
    tmpstr = "\n##acerpy_isnull_" + today + "\n" + \
             "##" + tmpstr + "\n" + \
             head + "IF cl_null(" + g_bgjob_g_bookno + ") OR " + g_bgjob_g_bookno + " = 'N'" + then
    return tmpstr


def doubleit(m):
    '''找到char定義，將長度放大兩倍'''
    head = m.group(1)
    L = m.group(2)
    tail = m.group(3)
    LL = str(int(L) * 2)
    tmpstr = head + LL + tail + '   ##原先char=' + L + ' ##acer_lza_' + today
    #
    return tmpstr


def doubleit_tempt(m):
    '''找到char定義，將長度放大兩倍'''
    head = m.group(1)
    body = m.group(2)
    tail = m.group(4)  # 3不是
    #
    find = '(.+char\()([0-9]+)(\).*)'
    pattern = re.compile(find, flags=re.I)
    body = pattern.sub(doubleit, body)
    #
    tmpstr = head + body + tail + '\n##acer_tempt_' + today + '\n'
    #
    return tmpstr


def inglang(m):
    '''處理在語系判斷中的open window'''
    tmpstr = m.group()
    # {%}會影響{}註解不全，先去除
    tmpstr = tmpstr.replace('{%}', '')
    # open後增加為4個space，以跟不在g_lang裡的區別
    pattern = re.compile('OPEN +WINDOW', flags=re.I)
    tmpstr = pattern.sub('OPEN    WINDOW', tmpstr)

    # openwindow----ex: asfi300
    pattern = re.compile('OPEN +WINDOW.+\n{0,1}.*WITH +FORM +"(.+?)".*', flags=re.I)
    m2 = pattern.search(tmpstr)  # 只要第一個匹配
    if m2:
        #  判斷主視窗cl_ui_init或子視窗cl_ui_locale
        formpath = m2.group(1)  # asf/frm/asfi300
        pcode = formpath.split('/')[-1]
        #
        find = '[a-z]{4}[0-9]{3}'
        pattern = re.compile(find, flags=re.I)
        m3 = pattern.match(pcode)
        #
        pattern = re.compile('.+', flags=re.I | re.S)  # re.S for . including \n
        replace = '\n##acerpy_clui_inglang_openwindow_' + today + '\n'
        replace += '{\n\g<0>\n}\n'
        replace += m2.group() + '\n'
        replace += 'CALL cl_ui_init()\n' if (m3 and len(pcode) == 7) else 'CALL cl_ui_locale("' + pcode + '")\n'
        replace += '##clui_over\n\n'
        tmpstr = pattern.sub(replace, tmpstr)
        #
        return tmpstr

    # call_menu----ex: asfi300
    pattern = re.compile('CALL.+?menu\( *?\).*', flags=re.I)
    m2 = pattern.search(tmpstr)  # 只要第一個匹配
    if m2:
        pattern = re.compile('.+', flags=re.I | re.S)  # re.S for . including \n
        replace = '\n##acerpy_clui_inglang_callmenu_' + today + '\n'
        replace += '{\n\g<0>\n}\n'
        replace += m2.group() + '\n'
        replace += ''  # 'CALL cl_ui_locale()\n'
        replace += '##clui_over\n\n'
        tmpstr = pattern.sub(replace, tmpstr)
        #
        return tmpstr
    #
    return tmpstr


def notinglang(m):
    '''處理不在語系判斷中的open window'''
    tmpstr = m.group()
    formpath = m.group(1)  # /u/hmk/lin/hun/frm/huni108
    pcode = formpath.split('/')[-1]
    #
    find = '[a-z]{4}[0-9]{3}'
    pattern = re.compile(find, flags=re.I)
    m2 = pattern.match(pcode)

    if m2 and len(pcode) == 7:  # 主視窗
        tmpstr += '\n\nCALL cl_ui_init()    ##acerpy_clui_init_' + today + '\n'
    else:
        tmpstr += '\n\nCALL cl_ui_locale("' + pcode + '")    ##acerpy_clui_locale_' + today + '\n'
    #
    return tmpstr


def worker(file_src, cleaner):
    '''thread的target'''
    file_name = os.path.basename(file_src)
    # 讀取處理
    with open(file_src, 'rb') as file_src_handler:
        content = file_src_handler.read()
        # print(content)
        for func in func_IN:
            if func == 'utf8':
                content = cleaner.__dict__[func].__func__(cleaner, content, file_name)
                if content == 'UnicodeDecodeError':
                    break
                continue
            content = cleaner.__dict__[func].__func__(cleaner, content)

    # 寫入處理
    file_tar = path_tar + '/' + os.path.basename(file_src)
    with open(file_tar, 'wb') as file_tar_handler:
        if '.4gl' in file_name:
            comment = "# " + today + " acer_python 處理項目: " + ','.join(func_IN) + "\n"
            comment += "##############################################################\n"
            content = comment + content
        finalbyte = content.encode('utf-8')
        file_tar_handler.write(finalbyte)
        # print(path_tar)


# tkinter
def file_ext_selection():
    global file_ext
    file_ext = var.get()
    cleaner_dict = dict(cleaner_ALL[file_ext].__dict__)
    cleaner_func = [funcname for funcname, obj in cleaner_dict.items() if isinstance(obj, classmethod)]
    func_ALL[file_ext] = cleaner_func

    # 造方法checkbox
    method_list.clear()
    # for widget in F_method.winfo_children():
    #     widget.destroy()
    for e in method_chkbtn_list:
        e.destroy()
    method_chkbtn_list.clear()
    #
    for e in func_ALL[file_ext]:
        method_list.append(tk.IntVar(value=1))  # value=1預設全勾
        method_chkbtn_list.append(
            tk.Checkbutton(
                F_method, text=e, variable=method_list[-1],
                onvalue=1, offvalue=0
                # ,command=print_selection
            )
        )
        method_chkbtn_list[-1].pack(side='left')

    # text區說明
    t.delete('1.0', 'end')
    t.insert('insert', '各處理方法說明如下\n\n')
    for e in cleaner_func:
        tmp = getattr(cleaner_ALL[file_ext], e).__doc__
        t.insert('insert', '█ ' + e + ' 的作用為:\n\n')
        t.insert('insert', tmp + '\n\n\n\n')


def start():
    global cleaner_ALL, func_ALL, func_IN, file_ext
    global path_src, path_tar
    global utf_err_ignore_OK, utf_err_ignore_NG

    # 檢查目錄
    path_src = check_slash(E_path.get())
    if not os.path.exists(path_src):
        tkinter.messagebox.showinfo(title='Error', message='目錄不存在，請重新輸入')
        E_path.focus_set()
        return

    # 清空文字框
    t.delete('1.0', 'end')
    utf_err_ignore_OK.clear()
    utf_err_ignore_NG.clear()
    func_IN.clear()
    #
    file_ext = var.get()

    for idx, m in enumerate(method_list):
        if m.get() == 1:
            func_IN.append(func_ALL[file_ext][idx])
    # 強制utf8第一執行
    if 'utf8' not in func_IN:
        func_IN = ['utf8'] + func_IN
    #
    folder_src = os.path.basename(path_src)
    path_src_up = path_src.strip(folder_src)
    path_tar = path_src_up + folder_src + '_py3_' + '_'.join(func_IN)
    if not os.path.exists(path_tar):
        os.mkdir(path_tar)
    #
    t.insert('insert', '====================== START =============================\n')
    start_time = time()
    #
    files_src = glob.glob(path_src + '/*.*')
    cleaner = cleaner_ALL[file_ext]
    # 每個檔案一個執行緒處理
    threads = []
    for file_src in files_src:
        thread = Thread(target=worker, args=(file_src, cleaner))
        threads.append(thread)
        thread.start()
        #
        file_name = os.path.basename(file_src)
        t.insert('insert', '開始處理: ' + file_name + '\n')
        t.see(tkinter.END)
        t.update_idletasks()
    for thread in threads:
        thread.join()
    #
    end_time = time()
    #
    t.insert('insert', '====================== END =============================\n')
    t.insert('insert', '輸出目錄: ' + path_tar + '\n')
    t.insert('insert', '共處理 ' + str(len(files_src)) + ' 個檔案\n')
    t.insert('insert', '共耗時 %.3f 秒' % (end_time - start_time) + '\n')
    #
    utf_err = utf_err_ignore_OK + [fn + ': 無處理' for fn in utf_err_ignore_NG]
    if utf_err:
        t.insert('insert', '------------- WARN -------------\n')
        t.insert('insert', '\n'.join(utf_err) + '\n')
        t.insert('insert', '------------- WARN -------------\n')
        t.insert('insert', str(set(byte_err)) + '\n')
        t.insert('insert', '1.以上WARN中' + str(len(utf_err)) + '個原始檔有以上非法字元的解碼問題\n')
        t.insert('insert', '2.WARN中註明<無處理>者，輸出檔僅告知UnicodeDecodeError\n' +
                 '  其餘則忽略解碼報錯，大部分可轉utf8成功，請留意輸出檔案是否OK\n')
    t.see(tkinter.END)
    t.update_idletasks()
    tkinter.messagebox.showinfo(title='OK', message='處理結束!')


# class
class toutf8():
    '''優先以big5解碼為unicode，供其他cleaner繼承'''
    # 非法字元可忽略解碼問題，轉unicode再編utf8正常
    ignore_OK_set = {'0xa1', '0xb2', '0xbb', '0xa5', '0xb5',
                     '0xb9', '0xc7', '0xf2', '0xf2', '0x91',
                     '0xaa', '0xed',
                     '0xee', '0xfb', '0xb8', '0xd9', '0xae',
                     '0xd7', '0xaa', '0xd3', '0xc4', '0xc6',
                     '0xdf', '0xf9'}
    # 非法字元不可忽略解碼問題
    ignore_NG_set = {'0xff', '0xfe', '0xa6', '0xb5'}  # '0xe5'

    @classmethod
    def utf8(cls, content, file_name):
        '''輸入bytes，輸出unicode，有解碼問題則該檔不處理'''
        try:
            content = content.decode('big5')
        except UnicodeDecodeError as err:
            m = re.findall('0x[a-zA-Z0-9]{2}', str(err))
            global byte_err
            byte_err += m  # 收集非法byte
            #
            if set(m) & cls.ignore_OK_set:
                utf_err_ignore_OK.append(file_name)
                content = content.decode('big5', 'ignore')
                # 忽略轉成空字串''

            elif set(m) & cls.ignore_NG_set:
                utf_err_ignore_NG.append(file_name)
                return 'UnicodeDecodeError'

            else:
                content = content.decode('utf-8')
        #
        return content


class fgl_cleaner(toutf8):
    '''處理4gl洗檔'''

    @classmethod
    def utf8(cls, content, file_name):
        '''輸入bytes，輸出unicode'''
        return super().utf8(content, file_name)

    @classmethod
    def refresh(cls, content):
        '''所有message及error下一行加CALL ui.Interface.refresh()'''
        find = '^[ \t]*(message|error) +(?!line).*'  # 最前面不一定是space，也有tab
        replace = '\n##acerpy_refresh_' + today + '\n' + \
                  '\g<0>\n' + \
                  'CALL ui.Interface.refresh()\n' + \
                  '##acerpy_refresh_over\n'
        pattern = re.compile(find, flags=re.I | re.M)
        content = pattern.sub(replace, content)
        #
        return content

    @classmethod
    def displayat(cls, content):
        ''' display ... at ...  改為message，只處理一共最多三行
        #DISPLAY g_msg AT 2,1 ATTRIBUTE(RED) ==>
        MESSAGE g_msg
        CALL ui.Interface.refresh()
        '''
        # 一行
        find = '^[^#\n]*display(.+)at +[0-9]+, *[0-9]+.*'  # at前面不一定是space，也有tab
        replace = '\n##acerpy_displayat_1_' + today + '\n' + \
                  '{\n\g<0>\n}\n' + \
                  'MESSAGE \g<1>\n' + \
                  'CALL ui.Interface.refresh()\n' + \
                  '##acerpy_displayat_over\n'
        pattern = re.compile(find, flags=re.I | re.M)
        content = pattern.sub(replace, content)

        # 二行
        find = '^[^#\n]*display(.+\n.+)at +[0-9]+, *[0-9]+.*'  # 執行過一行，第二行不會有display
        replace = '\n##acerpy_displayat_2_' + today + '\n' + \
                  '{\n\g<0>\n}\n' + \
                  'MESSAGE \g<1>\n' + \
                  'CALL ui.Interface.refresh()\n' + \
                  '##acerpy_displayat_over\n'
        pattern = re.compile(find, flags=re.I | re.M)
        content = pattern.sub(replace, content)

        # 三行
        find = '^[^#\n]*display(.+\n.+\n.+)at +[0-9]+, *[0-9]+.*'  # 執行過一二行，二三行不會有display
        replace = '\n##acerpy_displayat_3_' + today + '\n' + \
                  '{\n\g<0>\n}\n' + \
                  'MESSAGE \g<1>\n' + \
                  'CALL ui.Interface.refresh()\n' + \
                  '##acerpy_displayat_over\n'
        pattern = re.compile(find, flags=re.I | re.M)
        content = pattern.sub(replace, content)
        #
        return content

    @classmethod
    def isnull(cls, content):
        '''
		可能有g_bgjob,g_bookno，以cl_null判斷space及IS NULL
        IF g_bgjob = ' ' OR g_bgjob = 'N' ==> IF cl_null(g_bookno) OR g_bookno = 'N'
        '''
        find = "^([^#\n]*)if +((g_bgjob|g_bookno)) *= *' *'.*"  # re.M時，[^#]包括\n
        pattern = re.compile(find, flags=re.I | re.M)
        content = pattern.sub(checkthen, content)
        #
        return content

    @classmethod
    def noattr(cls, content):
        '''ATTRIBUTE(RED/REVERSE) ==> #ATTRIBUTE(RED/REVERSE)'''
        find = 'ATTRIBUTE *\(.+\)'
        replace = '##acerpy_noattr_' + today + ' \g<0>'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)
        #
        return content

    @classmethod
    def close(cls, content):
        '''新增ON ACTION CLOSE EXIT MENU'''
        find = '.*COMMAND.+esc.+'
        replace = '\nON ACTION CLOSE EXIT MENU  ##acerpy_close_' + today + '\n\n' + \
                  '\g<0>'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content, 1)  # 只匹配第一個esc
        #
        return content

    @classmethod
    def nohelp(cls, content):
        '''註解底下
        COMMAND "H.說明" HELP 32010 CALL showhelp(1)
        COMMAND KEY(INTERRUPT) LET INT_FLAG=0
        '''
        find = '.*COMMAND.+HELP.*\n{0,1}[ \t]*(?!COMMAND)CALL +showhelp.+'  # 最多兩行
        replace = '\n##acerpy_nohelp_' + today + '\n' + \
                  '{\n' + \
                  '\g<0>\n' + \
                  '}\n'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)
        # ---------------------------------------------------
        find = '.*COMMAND.+INTERRUPT.*\n{0,1}[ \t]*(?!COMMAND)LET +INT_FLAG.+'  # 最多兩行
        replace = '\n##acerpy_nohelp_' + today + '\n' + \
                  '{\n' + \
                  '\g<0>\n' + \
                  '}\n'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)
        return content

    @classmethod
    def lza(cls, content):
        '''放大兩倍&(結束)位移修正
        l_za05          CHAR(40), ==> l_za05          CHAR(80),
        g_x ARRAY[16] OF    CHAR(40), ==> g_x ARRAY[16] OF    CHAR(80),
        PRINT g_x[4] , ==> PRINT g_x[4] CLIPPED ,
        '''
        # l_za05定義放大
        find = '(.*l_za05 +char\()([0-9]+)(\).*)'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(doubleit, content)

        # g_x定義放大
        find = '(.*g_x +array\[[0-9]+\] +of +char\()([0-9]+)(\).*)'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(doubleit, content)

        # print g_x[4]加clipped
        find = '(.*)(print +g_x\[4\])(.*)'
        replace = '\g<1>\g<2> CLIPPED \g<3>\n\g<1>##acer_lza_' + today
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)

        #
        return content

    @classmethod
    def tempt(cls, content):
        ''' temp table裡面的char放大兩倍，如axmq999
        CREATE TEMP TABLE q999_file
        (
               t_r          SMALLINT,
               t_deptcode   CHAR(4),
               t_dept       CHAR(16),
               t_qty        DECIMAL(12,2),
               t_amount     DECIMAL(12,2),
               t_rate       DECIMAL(7,2),
               t_goal       DECIMAL(12,2)
        );
        '''
        find = '(create +temp +table[^(]+?\()((.|\n)+?)(\) *;)'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(doubleit_tempt, content)
        #
        return content

    @classmethod
    def dsmark(cls, content):
        '''因為cl_ui_init已包含cl_dsmark，所以要註解
        CALL cl_dsmark() ==> #CALL cl_dsmark()
        '''
        find = '.*call +cl_dsmark.*'
        replace = '#\g<0>  ##acerpy_dsmark_' + today
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)
        #
        return content

    @classmethod
    def clui(cls, content):
        '''處理cl_ui_init & cl_ui_locale'''
        # 1.cl_ui_init會關screen，所以之前不能close，會造成關兩次報錯
        find = '.*CLOSE WINDOW SCREEN.*'
        replace = '#\g<0>  ##acerpy_screen_' + today + '\n'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)

        # 2.處理在g_lang判斷式裡面的(asfi300)
        find = '.*IF +g_lang(.|\n)+?END +IF'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(inglang, content)

        # 3.處理不在g_lang判斷式裡的(huni108)
        find = '^[^#\n]*OPEN {1,2}WINDOW.*\n{0,1}[^#\n]*WITH +FORM +"(.+?)".*'
        pattern = re.compile(find, flags=re.I | re.M)
        content = pattern.sub(notinglang, content)

        #
        return content


class per_cleaner(toutf8):
    '''處理per洗檔'''

    @classmethod
    def utf8(cls, content, file_name):
        '''輸入bytes，輸出unicode'''
        return super().utf8(content, file_name)

    @classmethod
    def pernoremark(cls, content):
        ''' 刪除倒三角形以下 ▼---44-------##'''
        find = '^▼-+.+'  # 一定要 ^ (搭配re.M)，\xa1 在其他地方也有
        replace = '\n\n\n\n'
        pattern = re.compile(find, flags=re.I | re.M | re.S)
        content = pattern.sub(replace, content)
        #
        return content


class ffd_cleaner(toutf8):
    '''處理4fd洗檔'''

    @classmethod
    def utf8(cls, content, file_name):
        '''輸入bytes，輸出unicode'''
        return super().utf8(content, file_name)

    @classmethod
    def ffdblack(cls, content):
        '''color="XXX" ==> color="black" 一定要有value'''
        find = 'color=".+?"'
        replace = 'color="black"'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)
        #
        return content

    @classmethod
    def ffdreverse(cls, content):
        '''不reverse'''
        find = 'reverse="true"'
        replace = 'reverse="false"'
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)
        #
        return content

    @classmethod
    def ffdnotitle(cls, content):
        '''如"確認生產工單維護作業(asfi300)"由cl_ui_init在app視窗標題以變數顯示'''
        find = '<Label.+text=".+[a-z]{4}[0-9]{3,4}.*"/>'
        replace = ''
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content, 1)
        #
        find = '<Label.+text="\([0-9]{1,3}\)"/>'
        replace = ''
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content, 1)
        #
        return content


class link_cleaner(toutf8):
    '''處理ln洗檔'''

    @classmethod
    def utf8(cls, content, file_name):
        '''輸入bytes，輸出unicode'''
        return super().utf8(content, file_name)

    @classmethod
    def linkremove(cls, content):
        '''目前移除cl_dsmark'''
        find = '.+(cl_dsmark).+'  # 多個時 (cl_dsmark|q_gja)
        replace = ''
        pattern = re.compile(find, flags=re.I)
        content = pattern.sub(replace, content)
        #
        return content


# global
today = mytoday()
cleaner_ALL = {
    '1': fgl_cleaner, '2': per_cleaner,
    '3': ffd_cleaner, '4': link_cleaner
}
func_ALL = {
    '1': [],  # 4gl ['utf8', 'isnull', 'display'],
    '2': [],  # per ['utf8', 'pernoremark'],
    '3': [],  # 4fd ['utf8', 'ffdblack', 'ffdreverse', 'ffdnotitle']
    '4': []  # link ['utf8',linkremove']
}
func_IN = []
file_ext = '1'
path_src = path_tar = ''
utf_err_ignore_OK = []
utf_err_ignore_NG = []
byte_err = []
method_list = []
method_chkbtn_list = []

# main======================================
if __name__ == '__main__':
    # tkinter
    window = tk.Tk()
    window.title('HMK_v1.9_洗檔程式')
    window.geometry('850x500')
    window.minsize(850, 500)

    # 輸入目錄_________________________________________
    F_path = tk.Frame(window)
    F_path.pack(side='top', fill='x')
    L_path = tk.Label(F_path, text=r'輸入來源目錄絕對路徑 [ex: C:\path\...\4gl]:')
    L_path.pack(side='left')
    E_path = tk.Entry(F_path, bd=5)  # , validate='focusout', validatecommand=pathcheck)
    E_path.pack(fill='x')

    # 選擇檔案類型radio_________________________________________
    F_type = tk.Frame(window)
    F_type.pack(side='top', fill='x')
    L_type = tk.Label(F_type, text=r'選擇檔案類型:')
    L_type.pack(side='left')
    #
    var = tk.StringVar(None, "1")  # 預設4gl
    r1 = tk.Radiobutton(F_type, text='4gl', variable=var, value='1', command=file_ext_selection)
    r1.pack(side='left')
    r2 = tk.Radiobutton(F_type, text='per', variable=var, value='2', command=file_ext_selection)
    r2.pack(side='left')
    r3 = tk.Radiobutton(F_type, text='4fd', variable=var, value='3', command=file_ext_selection)
    r3.pack(side='left')
    r4 = tk.Radiobutton(F_type, text='link', variable=var, value='4', command=file_ext_selection)
    r4.pack(side='left')

    # 處理方法checkbox================================
    F_method = tk.Frame(window)
    F_method.pack(side='top', fill='x')
    L_method = tk.Label(F_method, text=r'勾選處理方法:')
    L_method.pack(side='left', fill='x')

    # 開始執行_______________________________________
    b = tk.Button(window, text='開 始 執 行',
                  font=('Arial', 12), width=10, fg='red', bg='yellow',
                  height=1, command=start)
    b.pack(padx=10, pady=10)
    #
    t = tk.Text(window, height=27)
    t.pack(side='bottom', fill='x', padx=10, pady=10)
    #
    # show預設4gl的checkbox
    file_ext_selection()

    window.mainloop()

    # # python xxx.py後，命令列詢問輸入以下參數
    # # 1.輸入來源目錄絕對路徑________________________________________
    # print('--- genero洗檔 with python ---\n')
    #
    # while True:
    #     sys.stdout.write(r'(1)輸入來源目錄絕對路徑 [ex: C:\path\...\4gl]:')
    #     sys.stdout.flush()
    #     path_src = sys.stdin.readline()
    #     path_src = check_slash(path_src)
    #     if not os.path.exists(path_src):
    #         print('### 目錄不存在，請重新輸入 ###')
    #         continue
    #     break
    #
    # # 2.選擇檔案類型________________________________________
    # while True:
    #     sys.stdout.write('(2)選擇檔案類型 1.4gl 2.per 3.4fd 4.link [ex: 1]:')
    #     sys.stdout.flush()
    #     file_ext = sys.stdin.readline()
    #     file_ext = file_ext.strip()
    #     if file_ext not in func_ALL:
    #         print('### 類型不存在，請重新輸入 ###')
    #         continue
    #     break
    #
    # # 3.輸入執行處理方法，以逗號分隔________________________________________
    # cleaner_dict = dict(cleaner_ALL[file_ext].__dict__)
    # cleaner_func = [funcname for funcname, obj in cleaner_dict.items() if isinstance(obj, classmethod)]
    # func_ALL[file_ext] = cleaner_func
    # print('(3)處理方法共有', ','.join(func_ALL[file_ext]), '\n   (utf8強制執行)')
    #
    # while True:
    #     sys.stdout.write('   只輸入以逗號分隔的所需處理方法，或 Enter 全部執行 [ex: utf8,noattr]:')
    #     sys.stdout.flush()
    #     func_IN = sys.stdin.readline()
    #     func_IN = func_IN.strip().split(',')
    #     if func_IN in [['all'], ['']]:
    #         func_IN = func_ALL[file_ext]
    #         break
    #     setALL = set(func_ALL[file_ext])
    #     setIN = set(func_IN)
    #     if len(setIN - setALL) > 0:
    #         print('### 無用處理方法', list(setIN - setALL), '請重新輸入 ###')
    #         continue
    #     func_IN = [func for func in func_ALL[file_ext] if func in func_IN]  # 照ALL中的順序
    #     # 強制utf8第一執行
    #     if 'utf8' not in func_IN:
    #         func_IN = ['utf8'] + func_IN
    #     func_IN.insert(0, func_IN.pop(func_IN.index('utf8')))
    #     break
    #
    # # 4.產生輸出目錄________________________________________
    # folder_src = os.path.basename(path_src)
    # path_src_up = path_src.strip(folder_src)
    # path_tar = path_src_up + folder_src + '_py3_' + '_'.join(func_IN)
    # if not os.path.exists(path_tar):
    #     os.mkdir(path_tar)
    #
    # # 5.開始處理________________________________________
    # print('====================== START =============================')
    # start = time()
    # files_src = glob.glob(path_src + '/*.*')
    # cleaner = cleaner_ALL[file_ext]
    # # 每個檔案一個執行緒處理
    # threads = []
    # for file_src in files_src:
    #     thread = Thread(target=worker, args=(file_src, cleaner))
    #     threads.append(thread)
    #     thread.start()
    # for thread in threads:
    #     thread.join()
    # #
    # end = time()
    # print('====================== END =============================')
    # print('輸出目錄: ', path_tar)
    # print('共處理 ', len(files_src), ' 個檔案')
    # print('共耗時 %.3f 秒' % (end - start))
    # utf_err = utf_err_ignore_OK + [fn + ': 無處理' for fn in utf_err_ignore_NG]
    #
    # if utf_err:
    #     print('------------- WARN -------------')
    #     print('\n'.join(utf_err))
    #     print('------------- WARN -------------')
    #     print(set(byte_err))
    #     print('1.以上', len(utf_err), '個原始檔有以上非法字元的解碼問題')
    #     print('2.註明<無處理>者，輸出檔僅告知UnicodeDecodeError\n' +
    #           '  其餘則忽略解碼報錯，大部分可轉utf8成功，請留意輸出檔案是否OK')
    #     print('3.注意: 以NotePad++開啟問題原始檔時，非法字元可能會以問號 ? 呈現\n' +
    #           '  手動轉utf8後，? 仍會保留')
    #     # input()
    #     #
    #     print('\n')
    #     sys.stdout.write('<請按Enter結束洗檔，或按 y 以Notepad++開啟以上解碼問題原始檔>: ')
    #     sys.stdout.flush()
    #     YN = sys.stdin.readline().strip()
    #     if YN == 'y':
    #         notepadexe = ['C:/Program Files (x86)/Notepad++/notepad++.exe']
    #         utf_err = utf_err_ignore_OK + utf_err_ignore_NG
    #         errfiles = [path_src + '/' + fn for fn in utf_err]
    #         args = notepadexe + errfiles
    #         #
    #         try:
    #             subprocess.Popen(args)
    #             print('\n<請按任意鍵結束程式..>')
    #             input()
    #         except FileNotFoundError:
    #             print('### notepad++的exe檔路徑有誤，請按任意鍵程式結束 ###')
    #             input()
    # else:
    #     print('\n<請按任意鍵結束程式...>')
    #     input()
