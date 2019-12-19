import matplotlib
import matplotlib.pyplot as plt

# change input file to easyprivacy to obtain graph for easyprivacy
def extract_data():
    result = {}
    with open("1_easylist_input.txt") as fi:
        for line in fi:
            string = line
            line = line.split(' ')
            if line[0] == 'Date:':
                month = line[4]
                year = line[7]
                if year in result.keys():
                    if month in result[year].keys():
                        result[year][month]+=1
                    else:
                        result[year].update({month:0})
                else:
                    result.update({year:{}})
            else:
                continue

        return result

# change savefig file to easyprivacy to obtain graph for easyprivacy
def graph_plot(result):
    font = {'family': 'Liberation Serif',
            'weight': 'normal',
            'size': 10
            }

    matplotlib.rcParams['axes.titlesize'] = 8
    matplotlib.rcParams['axes.labelsize'] = 8
    matplotlib.rc('font', **font)
    # matplotlib.rcParams['text.usetex'] = True
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['pdf.use14corefonts'] = True

    x1 = []
    y1 = []

    for year, monthList in result.items():
        for month,count in result[year].items():
            # print(month,year,count)
            y1.append(count)
            x1.append(str(month+year))

    plt.plot(x1, y1)

    plt.xlabel('Time')
    plt.xticks(x1, rotation='vertical',fontsize=7)
    plt.ylabel('Commit Count')
    plt.locator_params(axis='x', nbins=18)

    plt.legend()
    plt.tight_layout()
    plt.savefig('easylist_gitStats.pdf', format='pdf', dpi=1200)

    # plt.show()

result = extract_data()
graph_plot(result)
