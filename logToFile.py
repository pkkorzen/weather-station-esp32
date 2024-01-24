# Hey there,
#
# Just for the people that are interested for creating separate log files for each time the device reboots / deepsleeps, I have made the following alteration that keeps the logfiles from being overwritten every reboot/deepsleep. Notice that this solution does not need any time keeping (and therefore an internet connection to synchronize time). I hope that it helps anyone facing debugging issues on long running devices where serial connections over longer periods do not make sense. Cheers.




# Logging every console output to a file for debugging puroposes on long running solutions.
import io, os

esp32_files = os.listdir()

# Removing the other files that are not log files.
esp32_files.remove('main.py')
esp32_files.remove('boot.py')

# Determining the highest ending number of the log files in order to increase the number for the next log write (after reboot or deepsleep).
highest_number = 0

# The following is nested in a try statement, in order to create an initial log file.
try:
    for filename in esp32_files:
        temp_number = int(filename[8:-4])
        if temp_number >= highest_number:
            highest_number = temp_number
    print('last logfile number is:', highest_number)
    print('logging now on logfile number ', highest_number+1)
except:
    pass


class logToFile(io.IOBase):
    def __init__(self):
        pass
 
    def write(self, data):
        logFileName = 'logfile_{}.log'.format(highest_number+1)
        with open(logFileName, mode="a") as f:
            f.write(data)
        return len(data)
 
# now your console text output is saved into file
#os.dupterm(logToFile())
 
# disable logging to file
# os.dupterm(None)