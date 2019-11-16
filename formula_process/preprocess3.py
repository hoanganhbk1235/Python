
# coding: utf-8

# In[1]:


from sympy import *
from sympy.parsing.latex import parse_latex
from sympy.core.evaluate import evaluate
import sympy
import numpy as np
import pandas as pd
import re
import regex
import unicodedata

with open('requirement.txt','r') as f:
    keyword_request = f.read().splitlines()
with open('keyword.txt','r') as f:
    keyword_content = f.read().splitlines()
keyword=r'|'.join([i.strip() for i in sorted(keyword_content+keyword_request,reverse=True,key=lambda x:len(x))])
keyword 

# In[2]:


# function: represent Tree chart of formula
class Node:
    # khởi tạo class Node để chứa sơ đồ dạng cây của công thức
    def __init__(self,name,sympy,string,pos,no_symbol):
        # các phép toán ( mỗi phép toán là 1 node: +, ^)
        self.name=name
        # chua sympy cua chinh no
        self.sympy=sympy
        # chứa node con ( vd : a*x^2, a, x 2, ...)
        self.leaf=[]
        # biểu diễn số của công thức
        self.str=str(string)
        # vị trí của từng phần tử trong công thức
        self.pos=pos
        # no_symbol=False neu trong Node co chua symbol
        self.no_symbol=no_symbol
def forward(expr,root=[]):
    ''' 
    convert sympy thành 1 node
    input:
        + expr: công thức đầu vào
        + bol: mục đích để return True, False
        + root: vị trí của node hiện tại
        
    return:
        + return các node
    '''
    # expr=nsimplify(expr)
    # chứa các biến list boolen: thể  hiện việc các leaf có chứa symbol hay không   
    tmp1=[]
    # chứa list các node
    tmp2=[]
    
    for i,child in enumerate(expr.args):
        # i index
        # child: argument của công thưc (ax^2, ...)
        
        # vd: với từng trường hợp:
        # a*x^2 => gọi lại ham forward(a*x^2) => node cấp 1: * tương tung 2 con : a và x^2
        # node câp 2: ^ tương ứng 2 nhánh con: x và 2
        a,b=forward(child,root=root+[i])
        if b.name==expr.func and b.name in [Add, Mul]:
            tmp2.extend(b.leaf)
        else:
            tmp2.append(b)
        tmp1.append(a)
    for e,i in enumerate(tmp2):
        i.pos=root+[e]
        
    # trường hợp expr là 1 symbol (x , y, ...)
    if expr.is_symbol:
        return False,Node(expr,expr,expr,root,False)
    # trường hợp tất cả các leaf không chứa symbol - hệ số tự do (vd hệ số tự do : sqrt(3)/ 2,  1/2, ... )
    # trường hợp sqrt(3)/ 2 ta xem như 1 hệ số tự do
    elif all(tmp1):
        tmp=Node(expr.func,expr,expr,root,True)
        [tmp.leaf.append(i) for i in tmp2]
        return True,tmp
        # return True,Node(expr.func,expr,root,True)
    # trường hợp expr chứa hệ số tự do trả về cấu trúc tối giản (vd: x^2 => x và 2)
    # vd: sqrt(3) = 3^1/2  => 3 và 1/2 . trường hợp này ta có thể tối giản
    # (sqrt(3)/ 2)*x  => sqrt(3)/ 2 và x. số sqrt(3)/ 2 ta xem như 1 hệ số tự do
    else:
        tmp=Node(expr.func,expr,expr,root,False)
        [tmp.leaf.append(i) for i in tmp2]
        return False,tmp 
    
def backward(expr):
    # trường hợp expr ko có nhánh con thì return chính nó (vd: x, 2, 1/2, ...)
    if len(expr.leaf)==0:
        return expr.name
    # trường hợp là phương trình, ..
    else:
        args=[backward(i) for i in expr.leaf]
        args
        return expr.name(*args)


# In[3]:


def lay_danh_sach_bien(expr):
    ''' 
    convert sympy thành 1 node
    input:
        + expr: công thức đầu vào
        
    return:
        + return list các biến trong công thức
    '''
    # expr=nsimplify(expr)
    
    # tạo list ls_variable chứa các biến (symbol đơn lẻ) trong phương trình
    ls_variable = []
    # nếu expr là 1 symbol đơn nhất (vd: x, y, ...)
    # return chính nó
    if expr.is_symbol:
        return [expr]
    # trường hợp expr là phương trình (ax^n + bx + c = 0, ...) hoặc là 1 cụm biến không đơn nhất (x^2, ax^n, bx, ) và hệ số tự do (vd: c)
    else:
        # ta xét từng thành phần trong biểu thức( vd: ax^n, bx, c)
        for i,child in enumerate(expr.args):
            # i index
            # child: argument của công thưc (ax^2, ...)
            
            # vd: ax^2 ta đệ quy gọi chính hàm forward_variable(ax^2) để thực hiện tách (a và x^n => (x và n))
            # sau đó xét từng thành phần và return trả lại biến x
            ls_variable+=lay_danh_sach_bien(child)
    return list(set(ls_variable)) 


# In[4]:


def toi_gian_cong_thuc(expr,is_convert):
    # trường hợp expr ko có nhánh con thì return chính nó hoặc 1 nếu ko phải symbols
    if len(expr.leaf)==0:
        if not expr.name.is_symbol:
            if is_convert:
            # trường hợp không phải symbol: 2, 3, sqrt(2)/3, ....
            # convert hệ số này về 1
                return S.One
            else:
                return expr.sympy
        else:
            # trương hơp gia tri nay la symbol và không có các phần tử con như: x
            # thì trả về chính nó
            return expr.name

    #  giá trị biến gốc node hiện tại là: 2*x, x^2, x+ 2, ...
    else:
        # đối với các trường hợp giá trị là symbols và co các phần tử con: 
        # x^2 pow(x và 2), 2*x^2 mul(2 và x^2 pow(x và 2)), (x + 2 add(x và 2)), ...

        # xet dấu ở node chứa những giá trị của những giá trị đang xét: x^2, x + 2, ...
        # nếu nhưa nno_symbolode này là phép: + , *, thì sẽ đưa tham số is_convert = True  
        # trường hợp này ta sẽ đưa hệ số của biên về 1
        if  expr.name==Add or expr.name==Mul:
            is_convert=[True]*len(expr.leaf)
            # is_convert=True
        #  nếu là phép : ^, sqrt, ...., thì is_convert = False
        # trường hợp giữ nguyên hệ số (mặc định chính nó), gặp hệ số mũ vs is_convert = False ns sẽ ko convert về 1
        elif expr.name==Pow:
            is_convert=[True,False]
        else:
            is_convert=[False]*len(expr.leaf)
            # is_convert=False

        #  đối với trường hợp : 2*x, x^2, 2+x, ...
        # xét từng phần tử trong node của biến này, và dựa trên các gía trị của is_convert để quyết định convert hệ số hay không
        args=[toi_gian_cong_thuc(i,is_convert[e]) for e,i in enumerate(expr.leaf)]
        if expr.name==Add:
            args=list(set(args))
    # trả về các giá trị sau khi chuyển đổi
    return expr.name(*args)


# In[5]:


def trich_xuat_keyword(expr):
    if expr.name==Add:
        result=[i.str for i in expr.leaf if len(i.leaf)>0 or i.no_symbol]
        [result.extend(trich_xuat_keyword(i)) for i in expr.leaf ]
        return result
    else:
        result=[]
        if expr.name in [Mul, Pow,Rational]:
            for i in expr.leaf:
                if i.no_symbol:
                    if len(i.leaf)>0:
                        result.append(i.str)
                else:
                    result.extend(trich_xuat_keyword(i))
            result.append(expr.str)
        return result          


# In[6]:


def tien_xu_ly_latex(latex):
    '''
    input: latex is extracted in de_bai
    output: latex is remove the error character
    implement:
        + ['\\quad', '\\mathrm', '\\rm)','\\qquad,'] ->
        + (num) : ex((1), (2), ...)
        + num,num -> num.num :  ex(3,4 -> 3.4)
        + '≤' -> '\\leq'
        + '≥' -> '\\geq'
        + '–' -> '-'
        ...
    '''
    # convert character phrase: number,number = number.number
    r = r'[0-9],[0-9]'
    number_error_phrase = re.findall(r, latex)
    for i in range(len(number_error_phrase)):
        convert_phrase = number_error_phrase[i].replace(',', '.')
        latex = latex.replace(number_error_phrase[i], convert_phrase)
    
    # biến đổi các keyword không hợp lệ
    #latex = latex.replace(' ', '')parse_latex(
    latex=latex.replace(' ','')
    d={
        r'\\quad':'',
        r'(\\mathrm{)(.*?)(})':r'\2',
        r'({\\rm{)(.*?)(}})':r'\2',
        r'(\\rm{)(.*?)(})':r'\2',
        r'\\qquad':'',
        r'\\hfill':';',
        r'\\fill':';',
        r'\\widehat':'',
        r'\\hat':'',
        r'\\overparen':'',
        r'\\left':'',
        r'\\right':'',
        r'\\dfrac':r'\\frac',
        r'\\cr':';',
        r'\\operatorname{.*?}':r'',
        r'\([0-9]\)':'',
        r'\\text{(.*?)}':';',
        r'≤': r'\\leq',
        r'≥': r'\\geq',
        r'≠': r'=',
        r'\\neq': r'=',
        r'\\ne': r'=',
        r'–': '-',
        r'([\\]+)([A-Z]+)':r"\2",
        r'(^[a-z])?([A-Z]+)(^[a-z])?':r"\\\2",
        r'(\d)([.])(\d)':r'\1||\3',
        r'([\.]|[\']|[\"])':r'',
        r'(\d)([||])(\d)':r'\1.\3',        
        r'α':r'\\alpha', 
        r'β':r'\\beta',
        r'(\d)(\|\|)(\d)':r'\1.\3',
        r'((([\\\w]*)([\{\(]([\w\+\-\\\*\^]|(?4))*[\}\)]))|(\d+))(\\over)((([\\\w]*)([\{\(]([\w\+\-\\\*\^]|(?4))*[\}\)]))|(\d+))':r'\\frac{\1}{\8}',
        r'([\w]+)(\\over)([\w]+)':r'\\frac{\1}{\3}',
        r'(\\sqrt)([\w\*]+)([\+\-\*\^\w]*)':r'\1{\2}\3',
        r'(\\root)(\d+)(\\of)(\w+)':r'\\sqrt[\2]{\4}',
            #xu ly truong hop {cos^2}{x}
        r'([\{\(])*(\\sin|\\cos|\\tan|\\cot)([\^]\d+)([\}\)])*([{])*(([\w\+\-\\\*\^]+)(\w)(\d+[\'])*)([}])*':r'\1\2\7\8\4\3',
            #xu ly truong hop cos5^o12
        # r'(\\sin|\\cos|\\tan|\\cot)(\d+)(([\w\+\-\\\*\^]+)(\w)})*(\d+)*)':r'\1{\2\3}',
        r'và|với|biết|đúng|đề|để|khi|Với|Biết':r';'
    }

    for r in d.keys():
        latex=regex.sub(r,d[r],latex)   

    accept=r'[\+]|[\-]|[=]|[>]|[<]|\\leq|\\geq|\\sqrt|\\frac|\\sin|\\cos|\\tan|\\cot'
    
    if regex.search(accept,latex) is not None:
        return latex
    return ''


# In[7]:


def xac_dinh_cau_truc(latex):
    '''
    input:(str) latex is extracted from de_bai
    output: (bool, ls_pt)
        + True, ls_he_pt
        + False, ls_pt
    implement:
        + detect latex is equation system or equation, ... .
    '''
    pat = r'([\\\(\{])*(\\begin\s*)({array}|{matrix})(\s*{\w})?(.*?)(\\end\s*)({array}|{matrix})([\\\}\)])*'
    result={'pt':[],'hpt':[]}
    for l in regex.findall(pat,latex):
        result['hpt'].append(list(l)[4])
    latex=regex.sub(pat,r'',latex)
    
    pat = r'([\\\(\{\[])*(matrix)([\{\(]([\w\+\-\\\*\^\;\=\&\.\,]|(?3))*[\}\)])'
    for l in regex.findall(pat,latex):
        result['hpt'].append(list(l)[2][1:-1])
    latex=regex.sub(pat,r'',latex)
    
    result['pt']=cat_pt(latex)
    
    return result


# In[8]:


def cat_pt(latex_repaired):
    char_split = [',', ';', '&&', '&', '\\n', '\n']
    ls_formula=[latex_repaired]
    for ch in char_split:
        tmp = [i.split(ch) for i in ls_formula]
        ls_formula=[]
        [ls_formula.extend(i) for i in tmp]
    ls_formula=[i for i in ls_formula if len(i)>0]        
    return ls_formula


# In[9]:


def them_ky_tu_nhan_vao_pt(formula):
    '''
    input: formula is latext(ex: -3x ^ { 3 } - \frac {5} {2}  x ^ { 2 })*( - 3 x + 3))
    output: formula is latext(ex: -3*x ^ { 3 } - \frac {5} {2} * x ^ { 2 })*( - 3 *x + 3))
    '''
    # tìm các vị trí hệ số và biến  dấu hiệu nhận biết: 
    # \s+ (tra empty, space) phân các giữa ký tự số \d+ hoặc ksy tự số trong dấu {\d} và ký tự chữ [a-zA-Z]
    str_empty_para_var = re.findall('[\{]*\d+\s*[\}]*\s*[a-zA-Z]',formula)
    for i in range(len(str_empty_para_var)):
        len_substr = len(str_empty_para_var[i])
        idx_char = formula.find(str_empty_para_var[i])
        formula = formula[:idx_char+ len_substr - 1] + '*' + formula[idx_char + len_substr - 1:]
    return formula


# In[10]:


def tien_xu_ly_pt(formula):
    '''
    input:(str) formula is a equation
    output:(str) formuala is made normalize
        + "pt": formula is latex (ex: 3*x^{2} + 2*x + 4 = 0)
        + "key": the element of formula (ex: 3*x^{2}|+|2*x|+|4|=|0)
    impliment: convert
        + r'\\left':'',
        + r'\\right':'',
        + r'\\,': '',
        + remove space in the first and last statement
        + remove [';', ',', '.'] in the last statement
        + I expected one of these: ')' : remove '(' in the first statement
        
    '''
    char_r = {
        r'\\,': '',
        r'&&': ''
    }
    for ch in char_r.keys():
        formula = re.sub(ch, char_r[ch], formula)
    # xóa các ký tự thừa ở cuối ( endchar ) và đầu (startchar) chuỗi
    endchar= r'([\;]|[\,]|[\.]|[\=]|[\>]|[\<]|[\\]|[\(]|[\{]|[:]|\\leq|\\geq|\n|\\n)*$'
    startchar= r'^([\;]|[\,]|[\.]|[\=]|[\>]|[\<]|[\}]|[\)]|[:]|\\leq|\\geq|\n|\\n)*'
    formula=regex.sub(startchar,'',formula)
    formula=regex.sub(endchar,'',formula)
    formula=regex.sub(r'[\\]+',r'\\',formula)
    # check error of formuala
    a = ''
    try:
        f =  parse_latex(formula)
    # check lỗi cho trường hợp công thức không bắt duoc
    except Exception as e:
        a=e.args[0]
        a = a.replace("')'", ")")
        a = a.replace("'='", "=")
        a = a.split('\n')
        
        if a != '':
            if (a[0] == "I expected one of these: )") or (a[0] == "missing ) at ="):
                if formula.startswith('('):
                    formula = formula[1:]
                else:
                    return []
                parse_latex(formula)
            
    return formula


# In[11]:


def xu_ly_pt(formula_latex):
    '''
    input: (str) formula_latex is equation latex 
    ouput: (dict)
        + "pt_don_gian": (str) phương trình đơn giản 
        + "thanh_phan": ex('3*x^{2}|2*x|)
        + "keyword": (str) danh sách các keyword nhận biết phương trình or hệ phương trình
        + "variable_set": (str) danh sách các biến  cần tìm trong phương trình
        
    '''
    formula = tien_xu_ly_pt(formula_latex)
    # formula:{'pt':'3*x^{2} + 2*x + 4 = 0', 'key': '3*x^{2}|+|2*x|+|4|=|0'}
    # pt = parse_latex(formula)
    # pt_test = srepr(pt)
    # if 'Symbol' not in pt_test:
    #     with evaluate(False):
    #         pt = parse_latex(formula)
    # # convert sympy equation: Eq(ax+b = c) to ax + b - c
    # if pt.func in [Equality, GreaterThan, LessThan, StrictLessThan, StrictGreaterThan]:                
    #     pt = pt.args[0] - pt.args[1] + S.One - S.One
    # else:
    #     pt=pt + S.One - S.One
    with evaluate(False):
        pt = parse_latex(formula)
    if pt.func in [Equality, GreaterThan, LessThan, StrictLessThan, StrictGreaterThan]:                
        pt = pt.args[0] - pt.args[1]
    check,a=forward(pt)

    if a.name==Add:
        is_add=True
    else:
        is_add=False
    if a.name==Mul:
        is_mul=True
    else:
        is_mul=False
    # biểu diễn công thức ở dạng sơ đồ cây
    #pt_chuan_hoa, keyword_para = trich_xuat_keyword(a,is_add, is_forward_variablemul)
    pt_chuan_hoa= toi_gian_cong_thuc(a,any([is_add,is_mul,check]))
    keyword_para = trich_xuat_keyword(a)
    keyword_para=list(set(keyword_para))
    for i in range(len(keyword_para)):
        keyword_para[i]=keyword_para[i].replace(' ','')
        if keyword_para[i].startswith('-'):
            keyword_para[i]=keyword_para[i][1:]
    # tạo biến dict, var, chứa thông tin của 1 phương trình
    var = dict()
    # trường hợp biểu thức chỉ có số ko có ẩn, ta xem là bài tính giá trị biểu thức
        
    var['pt_don_gian'] = str(pt_chuan_hoa)
    var['thanh_phan'] = '|'.join(keyword_para)

    # trường hợp bất phương trình
    if ('\\leq' in formula) or ('\\geq' in formula) or ('<' in formula) or ('>' in formula):               
        # add số biến biến của phương trình        
        variable = lay_danh_sach_bien(pt_chuan_hoa)

        #ls_keyword_pt= []
        #ls_keyword_pt.append("bất phương trình")
        #var['keyword'] = "|".join(ls_keyword_pt)
        var['keyword'] = 'bất phương trình'
        var['ds_bien'] = "|".join([str(j) for j in set(variable)])

    else:
        # add số biến biến của phương trình       
        variable = lay_danh_sach_bien(pt_chuan_hoa)
        
        #ls_keyword_pt= []
        #ls_keyword_pt.append("phương trình")
        #ls_keyword_pt.append("số biến "+ str(len(set(variable))))
        #var['keyword'] = "|".join(ls_keyword_pt)
        var['keyword'] = 'phương trình'
        var['ds_bien'] = "|".join([str(j) for j in set(variable)])
    return var


# In[12]:


def xu_ly_he_pt(formula_latex):
    '''
    input: (str) is equation system latex
    ouput: (dict)
        + "pt_don_gian": (str) phương trình đơn giản 
        + "thanh_phan": ex('3*x^{2}|2*x|sqrt{5})
        + "keyword": (str) danh sách các keyword nhận biết phương trình or hệ phương trình
        + "variable_set": (str) danh sách các biến  cần tìm trong phương trình
    '''
    # tạo dict chứa thông tin cuar từng hệ phương trình
    var = dict()
    hpt_don_gian = []
    thanh_phan_hpt = []
    variable_hpt = []
    log=[]
    char_split = ['\\\\', '&', ';', ',']
    for ch in char_split:
        if ch in formula_latex:
            ls_pt = formula_latex.split(ch)
            ls_pt = [i for i in ls_pt if len(i)>0]
            break
    for pt in ls_pt:
        # tìm ký tự dấu "." ở vị trí tiếp theo DIgital none (ko phải số)
        pat='[.](\D)'
        pos=re.search(pat, pt)
        if pos is not None:
            pos=pos.start()
            pt =pt[:pos]+pt[pos+1:]
        # xoa khoang trang 2 dau chuoi
        pt = pt.strip()

        # xóa ký tự '{' nếu chỉ xuất hiện ở đầu chuỗi
        if  pt.startswith('{'):
            pt = pt[1:]
            
        try:
            pt_detail = xu_ly_pt(pt)
            hpt_don_gian.append(pt_detail['pt_don_gian'])
            thanh_phan_hpt+= pt_detail['thanh_phan'].split('|')
            variable_hpt+= pt_detail['ds_bien'].split('|')
        except Exception as e:
            try:
                log.append(e.args[0])
                print(e.args[0])
            except:
                log.append(str(e))
                print(e)
        
    var['pt_don_gian'] = "|".join([str(i) for i in hpt_don_gian])
    var['thanh_phan'] = "|".join(list(set(thanh_phan_hpt)))
    var['ds_bien'] = "|".join(list(set(variable_hpt)))
    var['keyword'] = "hệ|phương trình"
    return var,log


# In[13]:


def xu_ly_latex(de_bai):
    result=[]
    log = []
    for f in re.findall(r'\\\((.*?)\\\)',de_bai):
        f=tien_xu_ly_latex(f)
        if len(f)==0:
            continue
        d=xac_dinh_cau_truc(f)
        for pt in d['pt']:
            try:
                result.append(xu_ly_pt(pt))
            except Exception as e:
                try:
                    log.append(e.args[0])
                    print(e.args[0])
                except:
                    log.append(str(e))
                    print(e)
        for hpt in d['hpt']:
            r,l=xu_ly_he_pt(hpt)
            result.append(r)
            log.extend(l)

    return result,log


# In[14]:


def xu_ly_noi_dung_text(subject):
    '''
    input: 
        + subject: (str) đề bài toán
    ouput: (dict)
        + "requirement_sentences": (list)
            -) (str) các câu request_question nối với nhau bởi các ký tư: "|"
            -) (str) danh sách các keyword xác định các câu:request_question
                     ( các keyword chỉ xuất hiện trong request_question vừa được tìm thấy) cách nhau: "|"
            -) (str) danh sách các keyword đặc trưng của bài toán, được tìm trong request_question ("|")
        + "content_sentences":
            -) nội dung tương tự như phần "requirement_sentences"
    implement:
        
    '''
    # tách công thức latex từ đề bài
    subject=unicodedata.normalize('NFC',subject).lower()
    subject=regex.sub(r'\\\((.*?)\\\)','',subject)

    subject = subject.replace('\\(', "")
    subject = subject.replace('\\)', "")
    stms = subject.split('\\n')
    
    stms=np.concatenate([i.split('.') for i in stms])
    stms=np.concatenate([i.split(':') for i in stms])
    stms= [re.sub(r'\s+' ,' ',i.lower().strip()) for i in stms if len(i.strip())>0]
    
    # create a list, ls_key, contain the important keywords of subject
    ls_key = []
    # tìm các keyword đặc trưng trong câu: request
    

    for sentence in stms:  
        sentence_key = list(set(regex.findall(keyword,' '+sentence+' ')))

        # for key in keyword_content:
        #     # xét những keyword đứng độc lập, không có ký tự word đứng bên cạnh
        #     pat=r'(\W)'+key+r'(\W)' 
        #     # thực hiện: search, thêm 2 ký tự khoảng trắng vào đầu cuối chuỗi xét để tìm sự 
        #     # xuất hiện của keyword (pat) trong chuỗi sentence
        #     # nếu pat xuất hiện trong trong sentence thì sẽ trả vể not None
        #     if re.search(pat,' '+sentence+' ') is not None:
        #         sentence_key.append(key)
        if len(sentence_key)>0:
            ls_key_is_appeared = []
            for i in range(len(sentence_key)):
                for j in range(len(sentence_key)):
                    if i != j and sentence_key[i] in sentence_key[j].split(' '):
                        ls_key_is_appeared.append(sentence_key[i])
            key_final = list(set(sentence_key) - set(ls_key_is_appeared))

            ls_key.append(key_final)
    body={}
    for sentence_key in ls_key:
        sentence_key = [i.strip() for i in sentence_key if i!= '']
        # sentence_key = list(set(sentence_key))
        # intersection: tìm các phần tử giống nhau của 2 list
        if len(list(set(sentence_key).intersection(keyword_request)))>0:
            if 'requirement_sentences' not in body.keys():
                body['requirement_sentences']=[]
            body['requirement_sentences'].append('|'.join(sentence_key))            
        else:
            if 'content_sentences' not in body.keys():
                body['content_sentences']=[]
            body['content_sentences'].append('|'.join(sentence_key))
    return body


# In[15]:


def extract_keyword(de_bai):
    '''
    input: 
        + subject: str đề bài

    ouput: dict
        + "sentences": process_sentences
        + "equation": process_equation
    '''
    result = dict()
    keyword=xu_ly_noi_dung_text(de_bai)
    
    if len(keyword.keys())>0:
        result['sentences'] = keyword
    try:    
        equation,log = xu_ly_latex(de_bai)
        if equation != []:
            result['equation'] = equation
    except Exception as e:
        return result,[str(e)]

    return result, log

# a=r"""Bài 14. Cho hai số thực x > y > 0. Chứng minh \(x + \frac { 4 } { ( x - y ) ( y + 1 ) ^ { 2 } } \geq 3\)"""
# extract_keyword(a)