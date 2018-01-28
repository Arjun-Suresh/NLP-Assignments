import sys
import os
import re
import pprint

patterns = ["obfuscate\(\'(.*?)\'\,\'(.*?)\'\)",
            '(\w+)(\s*)(@|&.*;)(\s*)(\w+)(\s*).(\s*)(\w*)(\s*)(.|;)?(\s*)[eE][dD][uU]',
            '(\w+)(\s+)([aA][tT]|[wW][hH][eE][rR][eE])(\s+)(\w+)(\s*)(((\s+)([dD][oO][tTmM])(\s+))|(\.)|(\;))(\s*)(\w+)(\s*)(((\s+)([dD][oO][tTmM])(\s+))|(\.)|(\;))(\s*)[eE][dD][uU]',
            '(\w+)(\s+)([aA][tT]|[wW][hH][eE][rR][eE])(\s+)(\w+)(\s*)(((\s+)([dD][oO][tTmM])(\s+))|(\.)|(\;))(\s*)[eE][dD][uU]',
            '(\w.*?)@(.*?)(\.|\;)((-)?(\s*)[eE](\s*)(-)?(\s*)[dD](\s*)(-)?(\s*)[uU])']

phone_numbers = ['((\()?[0-9][0-9][0-9](\))?[- ]?[0-9][0-9][0-9][- ][0-9][0-9][0-9][0-9])\D+']

""" 
TODO
This function takes in a filename along with the file object (actually
a StringIO object) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""
def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        for pattern in patterns:
            matches = re.findall(pattern, line)
            if len(matches) == 0:
                continue
            if matches[0][0]=='Server':
                break
            word = '(\w+)'
            dot = '^(\s)*[dD][oO][tTmM](\s)*$'
            at = '(^[aA][tT]$|^[wW][hH][eE][rR][eE]$)'
            edu = '(^[eE][dD][uU]$)'
            if pattern == patterns[0]:
                obfuscatedList = matches[0]
                email=obfuscatedList[1]+'@'+obfuscatedList[0]
                res.append((name, 'e', email))
            else:
                for tuple in matches:
                    print tuple
                    print '\n'
                    newTuple = ()
                    for index in range(len(tuple)):
                        tupleVal = tuple[index]
                        tupleVal = tupleVal.replace('-', '')
                        w = re.findall(word, tupleVal)
                        d = re.findall(dot, tupleVal)
                        a = re.findall(at, tupleVal)
                        e = re.findall(edu, tupleVal)
                        if len(w) != 0 and len(d) == 0 and len(a) == 0 and len(e) == 0 and '&#' not in tupleVal:
                            newTuple = newTuple + (tupleVal,)
                    print line + '\n'
                    print newTuple
                    if len(newTuple) == 2:
                        email = '%s@%s.edu' % newTuple
                    else:
                        email = '%s@%s.%s.edu' % newTuple
                    res.append((name, 'e', email))
            break
        for pattern in phone_numbers:
            match=re.findall(pattern,line)
            if len(match)==0:
                continue
            numbers = ()
            for tuples in match:
                num = '[0-9]'
                for index in range(len(tuples)):
                    if len(re.findall(num,tuples[index])) != 0:
                        numbers = numbers+(tuples[index],)
            for number in numbers:
                number = number.replace('(','')
                number = number.replace(')', '')
                number = number.replace(' ', '')
                if number[3] != '-':
                    number = number[:3]+'-'+number[3:]
                if number[7] != '-':
                    number = number[:7]+'-'+number[7:]
                res.append((name, 'p', number))

    return res

"""
You should not need to edit this function, nor should you alter
its interfaces
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
