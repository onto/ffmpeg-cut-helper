#!/usr/bin/python

import sys
import getopt
import os
from datetime import datetime

#
# Arguments:
# -i input file
# -t file with timestamps to cut
# -o output file
#

def time_to_output_format(t):
    return t.strftime("%H:%M:%S.000")

def parse_timestamps_file(filename):
    file = open(filename, "r")

    times = []

    for line in file:
        time_pair = line.strip('\n').split(' ')

        try :
            time_first = datetime.strptime(time_pair[0], "%H:%M:%S")
        except ValueError:
                time_first = datetime.strptime(time_pair[0], "%M:%S")

        try:
            time_second = datetime.strptime(time_pair[1], "%H:%M:%S")
        except ValueError:
            time_second = datetime.strptime(time_pair[1], "%M:%S")

        times.append([time_first, time_second])

    times = sorted(times, key = lambda time_pair: time_pair[0])

    periods = []

    periods.append(["00:00:00.000", time_to_output_format(times[0][0])])
    for i in range(0,len(times)-1):
        duration = times[i+1][0] - times[i][1]
        time_duration = datetime.strptime(str(duration), "%H:%M:%S")

        periods.append([time_to_output_format(times[i][1]), time_to_output_format(time_duration)])
    periods.append([time_to_output_format(times[len(times)-1][1]), "99:59:59.999"])

    return periods

def run_ffmpeg_on_periods(inputfile, outputfile, periods):

    outputfiles = []

    part = 0
    for period in periods:
        outputfile_part = '{0}.part{1}.{2}'.format(outputfile, part, outputfile.split('.')[-1])
        ffmpeg_copy_command = 'ffmpeg -ss {0} -i {1} -t {2} -c copy {3}'.format(period[0], inputfile, period[1], outputfile_part)

        print(ffmpeg_copy_command)
        os.system(ffmpeg_copy_command)

        outputfiles.append(outputfile_part)

        part += 1

    outputjoinfilename = outputfile + '.join.txt';
    with open(outputjoinfilename, "w") as outputjoinfile:
        outputjoinfile.write('\n'.join(["file '{}'".format(_) for _ in outputfiles]))

    ffmpeg_concat_command = 'ffmpeg -f concat -i {0} -c copy {1}'.format(outputjoinfilename, outputfile)

    print(ffmpeg_concat_command)
    os.system(ffmpeg_concat_command)

    for outputfile_part in outputfiles:
        os.remove(outputfile_part)
    os.remove(outputjoinfilename)

def main(argv):
    inputfile = ''
    timestampsfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:t:o:")
    except getopt.GetoptError:
        print 'ffmpeg-cut-helper.py -i <inputfile> -t <timestampsfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'ffmpeg-cut-helper.py -i <inputfile> -t <timestampsfile> -o <outputfile>'
            sys.exit()
        elif opt =="-i":
            inputfile = arg
        elif opt =="-t":
            timestampsfile = arg
        elif opt =="-o":
            outputfile = arg

    periods = parse_timestamps_file(timestampsfile)

    run_ffmpeg_on_periods(inputfile, outputfile, periods)

if __name__ == "__main__":
    main(sys.argv[1:])