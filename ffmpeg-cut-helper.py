#!/usr/bin/env python3

import sys
import getopt
import os
from datetime import datetime



def die():
    sys.exit(1)


class Config:
    def __init__(self, argv):
        self.inputfile = None
        self.timestampsfile = None
        self.outputfile = None
        self.join = False
        self.encoding_parameters = "-c copy"
        try:
            opts, args = getopt.getopt(argv, "hji:t:o:c:")
        except getopt.GetoptError:
            Config.usage()
            die()
        for opt, arg in opts:
            if opt == '-h':
                Config.usage()
                die()
            elif opt == '-i':
                self.inputfile = arg
            elif opt == '-t':
                self.timestampsfile = arg
            elif opt == '-o':
                self.outputfile = arg
            elif opt == '-j':
                self.join = True
            elif opt == '-c':
                self.encoding_parameters = arg
        if not self.inputfile or not self.timestampsfile or not self.outputfile:
            print('Required parameter missing')
            die()
    def usage():
        print("""
Cut holes or extract regions from video file. A frontend to ffmpeg -ss/-to and concat demuxer.

ffmpeg-cut-helper.py  [-j]  [-c PARAMS]  -i INPUT_FILE  -t TIMESTAMPS_FILE  -o OUTPUT_FILE

  -i  input file
  -o  output file

  -t  timestamps file with following format:

      REGION1_START REGION1_END
      REGION2_START REGION2_END
      ...

      REGIONx_START and REGIONx_END are time positions in format HH:MM:SS

      The script will produce the output by omitting listed REGIONs from the output:
      [0:0:0.000 ; REGION1_START] + [REGION1_END ; REGION2_START] + [REGION2_END ; <end>]

  -j  reverse the notion of timestamps list: instead of cutting regions, include these regions
      I.e. the output will be:
      [REGION1_START ; REGION1_END] + [REGION2_START ; REGION2_END]

  -c  encoding parameters for audio and video to use instead of "-c copy"

  -h  show this usage note
  """)



def timestamp_str_to_time(timestamp_str):
    tokens = timestamp_str.split(':')
    if len(tokens) == 3:
        fmt = '%H:%M:%S'
    else:
        fmt = '%M:%S'
    return datetime.strptime(timestamp_str, fmt)


def time_to_output_format(t):
    return t.strftime("%H:%M:%S.000")


def parse_timestamps_file(filename, mode_join):
    file = open(filename, "r")

    times = []

    for line in file:
        time_pair = line.strip('\n').split(' ')
        if len(time_pair) == 2:
            times.append([ timestamp_str_to_time(time_pair[0]), timestamp_str_to_time(time_pair[1]) ])

    times = sorted(times, key = lambda time_pair: time_pair[0])

    periods = []

    if mode_join:
        for t in times:
            periods.append([time_to_output_format(t[0]), time_to_output_format(t[1])])
    else:
        periods.append(["00:00:00.000", time_to_output_format(times[0][0])])
        for i in range(0, len(times) - 1):
            periods.append([time_to_output_format(times[i][1]), time_to_output_format(times[i+1][0])])
        periods.append([time_to_output_format(times[-1][1]), "99:59:59.999"])

    return periods


def run_ffmpeg_on_periods(inputfile, outputfile, periods, encoding_parameters):
    outputfiles = []
    part = 0
    for period in periods:
        outputfile_part = '{0}.part{1}.{2}'.format(outputfile, part, outputfile.split('.')[-1])

        ffmpeg_copy_command = 'ffmpeg -y -loglevel 0 -ss {0} -to {2} -i {1} {4} {3}'.format(
                period[0], inputfile, period[1], outputfile_part, encoding_parameters)

        print(ffmpeg_copy_command)
        os.system(ffmpeg_copy_command)

        outputfiles.append(outputfile_part)
        part += 1

    outputjoinfilename = outputfile + '.join.txt';
    with open(outputjoinfilename, "w") as outputjoinfile:
        outputjoinfile.write('\n'.join(["file '{}'".format(_) for _ in outputfiles]))

    ffmpeg_concat_command = 'ffmpeg -loglevel 0 -f concat -i {0} -c copy {1}'.format(outputjoinfilename, outputfile)

    print(ffmpeg_concat_command)
    os.system(ffmpeg_concat_command)

    for outputfile_part in outputfiles:
        os.remove(outputfile_part)
    os.remove(outputjoinfilename)



def main(argv):
    config = Config(argv)
    periods = parse_timestamps_file(config.timestampsfile, config.join)
    run_ffmpeg_on_periods(config.inputfile, config.outputfile, periods, config.encoding_parameters)



if __name__ == "__main__":
    main(sys.argv[1:])
