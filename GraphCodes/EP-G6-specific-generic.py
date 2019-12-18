#!/usr/bin/env python
# coding: utf-8

# In[6]:


import tldextract
from adblockparser import AdblockRules
import re
import matplotlib.pyplot as plt
import numpy as np
import os, fnmatch

# In[11]:
def adblockparser_parse(rule_list):
    return AdblockRules(rule_list)


def return_domain(rule_line):
    if rule_line[-1] == '\\':  # case when @@||flashx.tv/js/jquery.min.js|\
        rule_line = rule_line[:-1]
    rule = []
    rule.append(rule_line)
    easylist_adblock_rules = adblockparser_parse(rule)
    domain = ''

    for r in easylist_adblock_rules.rules:
        y = r.rule_text
        x = y
        if x[:2] == '||':
            if '^' in x:
                split = x.index("^")
                x = x[2:split]
            else:
                x = x[2:]
        elif x[:1] == '|':  # check this why
            x = x[1:]

        domain = tldextract.extract(x).domain

    return domain


def check_if_valid_domain(hostname):
    if len(hostname) > 255:
        return False
    hostname = hostname.rstrip(".")
    allowed = re.compile('^[a-z0-9]([a-z0-9\-\_]{0,61}[a-z0-9])?$',
                         re.IGNORECASE)
    labels = hostname.split(".")

    # the TLD must not be all-numeric
    if re.match(r"^[0-9]+$", labels[-1]):
        return False

    return all(allowed.match(x) for x in labels)


def isBlock(rule):
    if rule[:2] == '@@':
        return False
    # elif '#@#' in rule:
    #     return False
    else:
        return True


def optionHasName(rule, name):
    if line.find("$") >= 0:
        option_separator_index = line.find("$")
        options_list = line[option_separator_index + 1:]
        while options_list != "":
            option_full = ""
            split = options_list.index(",") if "," in options_list else -1
            if split == -1:
                option_full = options_list
                options_list = ""
            else:
                option_full = options_list[:split]

            list_exists = option_full.index("=") if "=" in option_full else -1

            if list_exists == -1:
                if name in option_full:
                    return True
            else:
                option_name = option_full[:list_exists]
                if name in option_name:
                    return True

            options_list = options_list[split + 1:]
    return False


def isSpecific(line):
    if optionHasName(line, 'sitekey'):
        return True

    elif optionHasName(line, 'domain'):

        option_separator_index = line.find("$")
        options_list = line[option_separator_index + 1:]

        while options_list != "":
            option_full = ""
            split = options_list.index(",") if "," in options_list else -1
            if split == -1:
                option_full = options_list
                options_list = ""
            else:
                option_full = options_list[:split]

            list_exists = option_full.index("=") if "=" in option_full else -1

            if list_exists != -1:
                option_name = option_full[:list_exists]
                if option_name == 'domain':
                    domain_list = option_full[list_exists + 1].split('|')
                    block_flag = 0
                    for ele in domain_list:
                        if ele[0] != '~':
                            block_flag += 1
                    if block_flag == 0:
                        return False
                    else:
                        return True
            options_list = options_list[split + 1:]

    elif '##' in line:
        sep = line.find('##')
        if sep == 0:
            return False
        elif sep > 0:
            domains_extract = line[:sep]
            domains = domains_extract.split(',')
            block_flag = 0
            for ele in domains:
                if ele[0] != '~':
                    block_flag += 1
            if block_flag == 0:
                return False
            else:
                return True

    elif '#@#' in line:
        sep = line.find('#@#')
        if sep == 0:
            return False
        elif sep > 0:
            domains_extract = line[:sep]
            domains = domains_extract.split(',')
            block_flag = 0
            for ele in domains:
                if ele[0] != '~':
                    block_flag += 1
            if block_flag == 0:
                return False
            else:
                return True

    else:
        return False


def set_data(entry, specific, generic):
    global data
    global total
    details = entry.split("-")
    year = details[2]
    data.update({year: {'specific': [], 'generic': []}})

    # plot stacked histogram for all the partners vs options that are available
    specific_curr = len(specific)
    generic_curr = len(generic)
    total = specific_curr + generic_curr

    data[year]['specific'].append(specific_curr)
    data[year]['generic'].append(generic_curr)


def graph_gen(entry, years, specific, generic):
    ticks = np.arange(len(years))
    fig, ax = plt.subplots()

    specific = np.array(specific)
    generic = np.array(generic)

    ax.bar(ticks, specific, width=0.5, label='specific', bottom=generic, color='violet')

    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()
        ax.text(x + width / 6,
                y + height / 2,
                '{:.0f}'.format(height),
                fontsize='8',
                horizontalalignment='center',
                verticalalignment='center')

    ax.bar(ticks, generic, width=0.5, label='generic', color='gold')

    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()
        ax.text(x + width / 6,
                y + height / 2,
                '{:.0f}'.format(height),
                fontsize='8',
                horizontalalignment='center',
                verticalalignment='center')

    ax.set_xlabel('Years')
    plt.xticks(ticks, years)
    ax.set_ylabel('Count')
    plt.legend(loc='best')
    # plt.show()
    image_filename = 'easyprivacy-specific-generic' + '.png'
    plt.savefig(image_filename, bbox_inches='tight')


# In[12]:


listOfFiles = os.listdir(
    '/Users/prashanthikanniapanmurthy/Desktop/Evolution-of-tracker-blocking-lists/GraphCodes')
pattern = "processed-easyprivacy*.txt"

data = {}
total = 0
for entry in listOfFiles:
    if fnmatch.fnmatch(entry, pattern):
        with open(entry, "r") as fi:
            print("Running -->", entry)
            # clean_up_for_parser(entry)

        specific = []
        generic = []

        with open(entry) as fi:
            for line in fi:
                line = line.rstrip()

                # print("Line -->",line)

                if isSpecific(line):
                    if '#@#' in line:
                        specific.append(line)
                    elif isBlock(line):
                        specific.append(line)
                    else:
                        generic.append(line)

                else:
                    if '#@#' in line:
                        generic.append(line)
                    elif isBlock(line):
                        generic.append(line)
                    else:
                        specific.append(line)

        print(len(specific))
        print(len(generic))

        # print(generic)

        set_data(entry, specific, generic)

years = []
specific_total = []
generic_total = []

for year in sorted(data.keys()):
    print(year)
    years.append(year)
    specific_total.extend(data[year]['specific'])
    print(specific_total)
    generic_total.extend(data[year]['generic'])
    print(generic_total)

print(years)
graph_gen(entry, years, specific_total, generic_total)













