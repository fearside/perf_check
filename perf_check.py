#!/usr/bin/python
import ConfigParser, thread, time, subprocess, sys, os, re, calendar
from itertools import chain
try:
  from tabulate import tabulate
except:
  print 'ERR: Could not import tabulate, please install tabulate.'
  quit(1)



##
### Classes
##

## Variables/Arrays
#production_active_sections =['Production','-p']
#test_active_sections =['Test','-t']
#development_active_sections =['Development','-d']

def PreParseConfig(value):
  config = ConfigParser.ConfigParser()
  try:
    config.read(value)
    return True
  except:
    return False

#
## Screen handling
#

class screen:
  clear = '\033c'
  zero_pos = '\033[0;0H'
  
  '''
  # spinning_cursor
  ## This indicator is used when "warming" up the hosts, a.k.a. fetching initial host statuses.
  '''
  @classmethod
  def spinning_cursor(cls, *args):
    while True:
        for cursor in '|/-\\':
            yield cursor
  
  '''
  # Print result
  ## This class method is primarily used to redraw and print the usage table for arr_status array.
  '''
  @classmethod
  def print_result(cls, *args):
    # Star infinite loop
    global cycles
    
    while True:
      global arr_main_table
      global arr_status
      global arr_cswch
      global debug
      global arr_log_table
      try: 
        sys.stdout.write(Set.Terminal.Screen.NullPosition)
        sys.stdout.flush()
        Set.Terminal.Cursor.Off()
        if len(arr_main_table) > 0:
          try:
            cpu_usage = colorize.lightyellow(os.popen('ps -p %s -o pcpu=' % pid).read().strip())+' %'
          except:
            cpu_usage = 'N/A'
          
          sys.stdout.write('Time: ' + colorize.yellow(time.strftime('%H:%M:%S')) +\
                          ' MEM: ' + colorize.lightyellow(str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)) +\
                           ' kb CPU: ' + str(cpu_usage)+\
                           ' C: '+ colorize.yellow(str(cycles)) + ' ' + Threads.write_to_log() +'            \n')
          
          if debug == 0:
            sys.stdout.write(tabulate(arr_main_table, headers_main, tablefmt='psql', numalign='right', stralign='right', floatfmt='.2f') + screen.zero_pos)
          else:
            sys.stdout.write(tabulate(arr_main_table, headers_main, tablefmt='psql', numalign='right', stralign='right', floatfmt='.2f') + '\n')
            sys.stdout.write('DEBUG:: STATUS\n' + tabulate(arr_status, header_status, tablefmt='psql', numalign='right', stralign='right', floatfmt='.2f') + '\n')
            #sys.stdout.write('DEBUG:: Context Switching\n' + tabulate(arr_cswch, header_cswch, tablefmt='psql', numalign='right', stralign='right', floatfmt='.2f') + '\n')
            sys.stdout.write('DEBUG:: Logging table\n' + tabulate(arr_log_table, header_logtable, tablefmt='psql', numalign='right', stralign='right', floatfmt='.2f') + screen.zero_pos)
          sys.stdout.flush()
        time.sleep(0.5)
      except (KeyboardInterrupt):
        sys.stdout.write(Set.Terminal.Screen.Clear + "\b\bCTRL-C caught, program aborting.\n")
        sys.stdout.flush()
        Set.Terminal.Cursor.On()
        raise

#
## Help Information Class
#
class Help:
  @classmethod
  def Information(value):
    print '==> HELP <=='
    print 'Information:'
    print '     This script fetches and processes current load and used memory from specified host(s) in corresponding section of the supplied config file.'
    print 'Usage:\
          \n-t\tTEST, all hosts under the Test section.\
          \n-d\tDEVELOPMENT, all hosts under the Development section.\
          \n-p\tPRODUCTION, all hosts under the Production section.\
          \n-h\tThis help text.'
    print 'Example:\
           \n\t' + sys.argv[0] + ' -p config_file.conf'

#
## Support class
#

class Support:
  '''
  ## Subclass GENERATE
  # Is used to generate supportfunctions
  '''
  class Generate:
    # Trend function
    @classmethod
    def Trend(cls, value, old, *args):
      # Set value&old to float    
      value = float(value)
      old = float(old)
      # Simple if case to ensure proper data output
      if value < old:
        trend = -(old - value)
      elif value == old:
        trend = 0.00
      elif value > old:
        trend = (value - old)
               
      trend = round(trend, 2)
      #old = round(old, 2)
      
      if trend < 0.00:
        trend = colorize.green(str(trend))
      elif trend == 0.00:
        trend = colorize.lightyellow('0.00')
      elif trend > 0.00:
        trend = colorize.red('+') + colorize.red(str(trend))
      return str(trend)
    
    # Trend function, PERCENTAGE
    @classmethod
    def Trend_Percentage(cls, value, old, *args):
      # Set value&old to float    
      value = float(value)
      old = float(old)
      try:
        trend = (value/old) * 100.00
      except ZeroDivisionError:
        trend = 100.00
      
      if trend < 100.00:
        trend = 100.00 - trend
      elif trend == 100.00:
        trend = 100.00
      elif trend > 100.00:
        trend = trend - 100.00
      
      trend = round(trend, 2)
      
      if trend < 100.00:
        trend = colorize.green('-' + str(trend)) + colorize.blue(' %')
      elif trend == 100.00:
        trend = colorize.lightyellow('0.00') + colorize.blue(' %')
      elif trend > 100.00:
        trend = colorize.red('+' + str(trend)) + colorize.blue(' %')
      return str(trend)
#
## Set class
#
class Set:
  '''
  # Set terminal stuff
  '''
  #@classmethod
  class Terminal:
    # Sub-class Screen
    class Screen:
      Clear = '\033c'
      NullPosition = '\033[0;0H'
    # Sub-class Cursor
    class Cursor:
      @classmethod
      def Off(value):
        os.system('setterm -cursor off')
      @classmethod
      def On(value):
        os.system('setterm -cursor on')

#
## Dynamic coloring
#
class colorize:
  
  #
  ## Base colors defined
  #
  
  MGT = '\033[95m'
  PRP = '\033[35m'
  BLU = '\033[34m'
  LBL = '\033[94m'
  CYN = '\033[36m'
  YLW = '\033[33m'
  LYW = '\033[93m'
  RED = '\033[31m'
  LRD = '\033[91m'
  GRN = '\033[32m'
  LGN = '\033[92m'
  EC  = '\033[0m'
  BLD = '\033[1m'
  UDL = '\033[4m'
  
  #
  ## Class: base coloring of input string
  #
  
  # Colorize magenta
  # Return a string which is colorized and neutralized after
  @classmethod
  def magenta(cls, value, *args):
    value = cls.MGT + str(value) + cls.EC
    return value
  
  # Colorize purple
  # Return a string which is colorized and neutralized after
  @classmethod
  def purple(cls, value, *args):
    value = cls.PRP + str(value) + cls.EC
    return value
  
  # Colorize yellow
  # Return a string which is colorized and neutralized after
  @classmethod
  def yellow(cls, value, *args):
    value = cls.YLW + str(value) + cls.EC
    return value
  
  # Colorize blue
  # Return a string which is colorized and neutralized after
  @classmethod
  def blue(cls, value, *args):
    value = cls.BLU + str(value) + cls.EC
    return value
  
  # Colorize red
  # Return a string which is colorized and neutralized after
  @classmethod
  def red(cls, value, *args):
    value = cls.RED + str(value) + cls.EC
    return value
  
  # Colorize green
  # Return a string which is colorized and neutralized after
  @classmethod
  def green(cls, value, *args):
    value = cls.GRN + str(value) + cls.EC
    return value
  
  # Colorize light red
  # Return a string which is colorized and neutralized after
  @classmethod
  def lightred(cls, value, *args):
    value = cls.LRD + str(value) + cls.EC
    return value
  
  # Colorize cyan
  # Return a string which is colorized and neutralized after
  @classmethod
  def cyan(cls, value, *args):
    value = cls.CYN + str(value) + cls.EC
    return value
  
  # Colorize light green
  # Return a string which is colorized and neutralized after
  @classmethod
  def lightgreen(cls, value, *args):
    value = cls.LGN + str(value) + cls.EC
    return value
  
  # Colorize light yellow
  # Return a string which is colorized and neutralized after
  @classmethod
  def lightyellow(cls, value, *args):
    value = cls.LYW + str(value) + cls.EC
    return value
  
  # Colorize light blue
  # Return a string which is colorized and neutralized after
  @classmethod
  def lightblue(cls, value, *args):
    value = cls.LBL + str(value) + cls.EC
    return value
  
  # Colorize neutral
  # Return a string which is colorized and neutralized after
  @classmethod
  def neutral(cls, value, *args):
    value = cls.EC + str(value) + cls.EC
    return value
  
  '''
  #
  ## Input chosen coloring
  #
   
  ## Colorize USED MEMORY/memory PROCENTAGE(%)
  #
  # Less than 5%  = RED
  # Less than 10% = LIGHT RED
  # Less than 15% = YELLOW
  # Less than 25% = LIGHT YELLOW
  # More than 25% = GREEN(OK)
  #
  # Method also converts free amount to used amount
  # Method also converts number from 1.00 to 100.00 by multiplying value with 100.
  #
  '''
  @classmethod
  def mem_procentage_used(cls, value, *args):
    value = 1.00 - float(value)
    if float(value) < 0.75:
      value = cls.green(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) <= 0.75:
      value = cls.lightyellow(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) <= 0.85:
      value = cls.yellow(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) <= 0.95:
      value = cls.lightred(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) > 0.95:
      value = cls.red(cls.set_decimals(cls.conv_to_100(value)))
    return value
  
  '''
  ## Colorize FREE MEMORY/memory PROCENTAGE(%)
  #
  # Less than 5%  = RED
  # Less than 10% = LIGHT RED
  # Less than 15% = YELLOW
  # Less than 25% = LIGHT YELLOW
  # More than 25% = GREEN(OK)
  #
  # Method also converts number from 1.00 to 100.00 by multiplying value with 100.
  #
  '''
  @classmethod
  def mem_procentage_free(cls, value, *args):
    if float(value) <= 0.05:
      value = cls.red(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) <= 0.10:
      value = cls.lightred(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) <= 0.15:
      value = cls.yellow(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) <= 0.25:
      value = cls.lightyellow(cls.set_decimals(cls.conv_to_100(value)))
    elif float(value) > 0.25:
      value = cls.green(cls.set_decimals(cls.conv_to_100(value)))
    return value
   
   
  '''
  ## Colorize LOAD/load usage
  #
  # value = load
  # total_value = cpus
  # 
  # Clarification of statements:
  #
  # Load equal or less than 1   (100%) x CPU(s) = GREEN(OK)
  # Load equal or less than 1.25(125%) x CPU(s) = LIGHT YELLOW
  # Load equal or less than 1.5 (150%) x CPU(s) = YELLOW
  # Load equal or less than 1.75(175%) x CPU(s) = LIGHT RED
  # Load equal or MORE than 1.75(175%) x CPU(s) = RED
  #
  '''
  @classmethod
  def load(cls, value, total_value, *args):
    if float(value) <= total_value:
      value = cls.green(value)
    elif float(value) <= total_value * 1.25:
      value = cls.lightyellow(value)
    elif float(value) <= total_value * 1.5:
      value = cls.yellow(value)
    elif float(value) <= total_value * 1.75:
      value = cls.lightred(value)
    elif float(value) > total_value * 1.75:
      value = cls.red(value)
    return value
  
  '''
  # Colorizer ERROR COUNT
  #
  # Equal to  0 = GREEN 
  # More than 0 = RED
  #
  '''
  @classmethod
  def err_count(cls, value, *args):
    if int(value) == 0:
      value = cls.green(value)
    elif int(value) > 0:
      value = cls.red(value)
    return value
  
  '''
  ## Strip all decimals but 2, 0.01234 to 0.01
  # Support method
  '''
  @classmethod
  def set_decimals(cls, value, *args):
    dec = '1'
    if args:
      for arg in args:
       if arg:
         dec = str(arg)
    value = format(value, '.' + dec + 'f')
    return value
    
  '''
  ## Convert 0.10 to 10.00
  # Support method
  '''
  @classmethod
  def conv_to_100(cls, value, *args):
    value = value * 100
    return value

    
class Threads:
  '''
  ## Fetch context switching
  # Thread method
  '''
  @classmethod
  def fetch_cswch(cls, threadName, delay, server, *args):
    count = 0 # Local cycle count, also used to warm up host
    count_calc = 1 # Local average counter for trending value
    while True:      
      try:
        global arr_cswch
        
        ssh = subprocess.Popen(["ssh", "%s" % server, CMD_CSWCH], shell=False, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cswch = list(chain(*[element.strip().split(';') for element in ssh.stdout.readlines()]))
        ssh.terminate()
        ssh.poll()
        
        if count > 0:
          time.sleep(delay)
        if count == 0: # Look if the while case is running for the first time, local variable
          result = [server,float(cswch[0]),float(cswch[0]),float(cswch[0]),count_calc]
          arr_cswch.append(result) # Append the array with the hosts index
          count += 1
          time.sleep(delay)
        else:  
          for i in range(len(arr_cswch)): # Loop through indexes
            if server == arr_cswch[i][0]: # Find the correct index in array
              arr_cswch[i][4] += 1 # Counted value
              arr_cswch[i][2] = float(arr_cswch[i][2]) + float(arr_cswch[i][1]) # Total value
              arr_cswch[i][3] = float(arr_cswch[i][2]) / float(arr_cswch[i][4]) # divided value
              arr_cswch[i][1] = float(cswch[0]) # Current value           
        
      except (KeyboardInterrupt):
        sys.stdout.write(Set.Terminal.Screen.Clear + "\b\bInternal CTRL-C caught, program aborting.\n")
        sys.stdout.flush()
        Set.Terminal.Cursor.On()
        raise
      except IndexError, e: # Added for debugging purpose, this usually occurs when the ssh subprocess is fetching the data from one host.
        print screen.clear + "Index error[subprocess][cmd_cswch][" + server + "]["+str(count)+"] :", e
        print ''
        Set.Terminal.Cursor.On()
        # Bug fix, we now raise a SystemExit to properly exit the application instead of just leave it hanging.
        raise SystemExit(97)
      except Exception, e: # Added for debugging purpose, this usually occurs when the ssh subprocess is fetching the data from one host.
        print screen.clear + "Application error[subprocess][cmd_cswch][" + server + "]["+str(count)+"] :", e
        print ''
        Set.Terminal.Cursor.On()
        # Bug fix, we now raise a SystemExit to properly exit the application instead of just leave it hanging.
        raise SystemExit(96)
  
  
  '''
  # 
  ## Generate table classmethod
  #
  '''
  @classmethod
  def generate_table(cls, threadName, delay, server, *args):
    count = 0 # Local cycle count, also used to warm up host
    while True:
      if count == 0:
        time.sleep(delay)
      # Global values/arrays
      global arr_cswch
      global arr_status
      global arr_main_table
      global cycles
      cycles += 1
      # Define helper variables
      result = []
      cswch = '-'
      trend_cswch = '-'
      cswch_total = '-'
           
      # Context-Switching
      if len(arr_cswch) > 0:
        for i in range(len(arr_cswch)):
          # Find the correct index in array
          if server == arr_cswch[i][0]:
            cswch = arr_cswch[i][1]
            cswch_old = arr_cswch[i][3]
            cswch_total = arr_cswch[i][2]
          
          if cswch != '-':
            cswch_total = arr_cswch[i][2]
            trend_cswch = Support.Generate.Trend_Percentage(cswch,cswch_old)
        
      # Status data MEM/LOAD
      if len(arr_status) > 0:
        for i in range(len(arr_status)): # Loop through indexes
          if server == arr_status[i][0]: # Find the correct index in array
            cpus       = arr_status[i][5]
            load_now   = colorize.load(arr_status[i][1], cpus)
            load_5min  = colorize.load(arr_status[i][2], cpus)
            load_trend = Support.Generate.Trend(arr_status[i][1], arr_status[i][3])
            mem_usage  = colorize.mem_procentage_used(arr_status[i][4])
            cpus       = colorize.yellow(int(cpus))
            

      # Build result array
      try:
        result = [ server, cpus, load_now, load_5min, load_trend, mem_usage, cswch, trend_cswch ]
      except:
        pass
         
      if count > 0:
          time.sleep(delay)
        
      if count == 0: # Look if the while case is running for the first time, local variable
        if len(result) > 0:
          arr_main_table.append(result) # Append the array with the hosts index
          count += 1
          time.sleep(delay)
      else:
        for i in range(len(arr_main_table)): # Loop through indexes
          if server == arr_main_table[i][0]: # Find the correct index in array
            arr_main_table[i] = result # Update index in array
            
      
  '''
  # 
  ## fetch method
  #
  '''
  @classmethod
  def fetch_status(cls, threadName, delay, server, *args):
    count = 0 # Local cycle count, also used to warm up host
    log_count = 0
    time_past = calendar.timegm(time.gmtime())
    # Fetch and parse number of CPUs from server
    try:
      cpu_check = subprocess.Popen(["ssh", "%s" % server, CMD_CPUS], shell=False, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      cpus = [element.strip() for element in cpu_check.stdout.readlines() ]
      cpus = float(cpus[0])
      cpu_check.terminate()
      cpu_check.poll()
      del cpu_check
    except:
      cpus = 1.00

    while True: # Star infinite loop 
      try:
        global arr_status
        global arr_log_table
        ssh = subprocess.Popen(["ssh", "%s" % server, CMD_STATUS], shell=False, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = list(chain(*[element.strip().split(';') for element in ssh.stdout.readlines()]))
        ssh.terminate()
        ssh.poll()
        
        # If first value(s) already has been fetched, sleep for a couple of seconds
        if count > 0:
          time.sleep(delay)
        
        # Generate / Set values for array
        mem_usage = (float(result[6]) + float(result[7]) + float(result[8])) / float(result[5]) # Calculate used memory in percentage
        mem_used = float(result[6]) + float(result[7]) + float(result[8])
        mem_total = float(result[5])
        mem_free = mem_total - mem_used
        time_update = time.strftime('%H:%M:%S')                           # Colorize time
        
        l_now = result[0]
        l_5min = result[1]
        l_15min = result[2]
        
        
        # Build result array
        result = [ server, result[0], result[1], result[2], mem_usage, cpus, time_update ]
        # Append log array
        time_now = calendar.timegm(time.gmtime())
        if (time_now - time_past) > 14:
          arr_log_table.append([ time.strftime('%Y-%m-%d %H:%M:%S'), server, int(cpus), l_now, l_5min, l_15min, mem_free, mem_total ])
          time_past = calendar.timegm(time.gmtime())
        
        if count == 0: # Look if the while case is running for the first time, local variable
          arr_status.append(result) # Append the array with the hosts index
          count += 1
          time.sleep(delay)
        else:
          for i in range(len(arr_status)): # Loop through indexes
            if server == arr_status[i][0]: # Find the correct index in array
              arr_status[i] = result # Update index in array     
      except (KeyboardInterrupt):
        sys.stdout.write(Set.Terminal.Screen.Clear + "\b\bInternal CTRL-C caught, program aborting.\n")
        sys.stdout.flush()
        Set.Terminal.Cursor.On()
        raise
      except IndexError, e: # Added for debugging purpose, this usually occurs when the ssh subprocess is fetching the data from one host.
        print screen.clear + "Index error[subprocess][cmd_load][" + server + "]["+str(count)+"] :", e
        print ''
        Set.Terminal.Cursor.On()
        # Bug fix, we now raise a SystemExit to properly exit the application instead of just leave it hanging.
        raise #SystemExit(97)
      except Exception, e: # Added for debugging purpose, this usually occurs when the ssh subprocess is fetching the data from one host.
        print screen.clear + "Application error[subprocess][cmd_load][" + server + "]["+str(count)+"] :", e
        print ''
        Set.Terminal.Cursor.On()
        # Bug fix, we now raise a SystemExit to properly exit the application instead of just leave it hanging.
        raise SystemExit(96)

  @classmethod
  def write_to_log(cls, *args):
    global arr_log_table
    global log_location
    if len(arr_log_table) > 100:
      local_log_table = arr_log_table
      arr_log_table = []
      local_log_table.reverse()
      try:
        logfile = open(log_location,'a')
        for row in range(len(local_log_table)):
          log_row = ';'.join(map(str,local_log_table.pop()))+'\n'
          logfile.write(log_row)
        logfile.close()
      except Exception, e:
        print screen.clear + 'Application error[subprocess][WriteToLog] : ', e
        raise
      return str(colorize.red('LOG WRITE'))
    else:
      return str(len(arr_log_table))
      #return str('')
      
  
  @classmethod
  def write_to_log_on_exit(cls, *args):
    global arr_log_table
    global log_location
    arr_log_table.reverse()
    try:
      logfile = open(log_location,'a')
      for row in range(len(arr_log_table)):
        log_row = ';'.join(map(str,arr_log_table.pop()))+'\n'
        logfile.write(log_row)  
      logfile.close()
      sys.stdout.write("Last rows in logging table written\n")
      sys.stdout.flush()
    except Exception, e:
      print screen.clear + 'Application error[subprocess][WriteToLogOnExit] : ', e
      raise
##
# End of classes and definitions
##

# Global variables 
CMD_STATUS="echo $(cat /proc/loadavg | tr -d '\n' | tr ' ' ';')';'$(cat /proc/meminfo | grep -E 'Buffers|^Cached|MemFree|MemTotal' | awk '{print $2}' |tr '\n' ';' | sed -e 's/\;$//1')"
CMD_CSWCH="sar -w 1 10 | grep 'Average:' | awk '{print $3}'"
CMD_CPUS="nproc"
pid = os.getpid()
arr_status = [] # Load and mem stats
arr_cswch = [] # Context switching stats
arr_main_table = [] # Main output table
arr_log_table = [] # Main logging table
log_location = '/var/log/perf_stats_'
return_code=0
serv_count=0
spin_count=0
cycles=0
debug = 0

# System argument options
production_active_sections =['Production','-p']
test_active_sections =['Test','-t']
development_active_sections =['Development','-d']
debug_active_sections = []

# Table, column names
headers_main = [ colorize.cyan('Server'),
          colorize.cyan('CPU(s)'),
          colorize.cyan('   Now'),
          colorize.cyan('  5min'),
          colorize.cyan('Tr./Load'),
          colorize.cyan('Used Mem %'),
          colorize.cyan('cswch/s'),
          colorize.cyan('Tr./cswch')]

header_status = ['Server','Now','5min','15min','Mem Usage','CPUS','Time Update']
header_cswch =  ['Server','Current','Total','Average','Count']
header_logtable = ['Date & Time','Server','NPROC','Now','5min','15min','M.FREE','M.TOTAL']
###########################
# Main script 
###########################

Set.Terminal.Cursor.Off()

# Loop through system arguments and parse config file
if len(sys.argv) > 2:
  if os.path.exists(sys.argv[2]) == False:
    print 'ERROR, Not a valid config file.'
    quit(98)
  elif PreParseConfig(sys.argv[2]) == False:
    print 'ERROR, can not parse config file.'
    quit(97)
  elif re.match('\-[dpt]\Z', sys.argv[1]) and PreParseConfig(sys.argv[2]) == True:      
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[2])
  else:
    print 'Bad formatting of arguments.'
    print 'Please consult the help(-h) section for proper usage.'
    Set.Terminal.Cursor.On()
    quit(96)
elif len(sys.argv) == 2:
  if re.match('\-[h]\Z', sys.argv[1]):
    Help.Information()
    Set.Terminal.Cursor.On()
    quit(0)
  elif re.match('\-[a-gi-z]\Z', sys.argv[1]):
    Help.Information()
    print '\nError:\nBad argument',sys.argv[1]
    Set.Terminal.Cursor.On()
    quit(0)
else:
  print 'Improper argument(s) given.'
  print 'Please consult the help(-h) section for proper usage.'
  Set.Terminal.Cursor.On()
  quit(94)

# Should be moved to an own classmethod
# Loop through/Parse all sections in config
for section in config.sections():
  for option in config.options(section):
    if str.lower(config.get(section, option)) == 'on':
      if str.lower(section) == 'production':
        production_active_sections.append(option)
        #log_location += '_production'
      if str.lower(section) == 'test':
        test_active_sections.append(option)
        #log_location += '_test'
      if str.lower(section) == 'development':
        development_active_sections.append(option)
        #log_location += '_development'
      if str.lower(section) == 'debug':
        if str.lower(option) in ["production", "test", "development"]:
          debug_active_sections.append(option)

# Should be moved to an own classmethod
# Set section and set servers from config file 
for section in production_active_sections, development_active_sections, test_active_sections:
  if len(section) > 2:
    if sys.argv[1] == section[1]:
      current_section = section[0]
      serv_list = section[2:]
      for debug_section in debug_active_sections: 
        if debug_section == str.lower(section[0]):
          debug = 1


print 'Environment,', current_section
log_location += str.lower(current_section)

# Should be moved to an own classmethod
# Start all sub-threads that fetches/processes information.
try:  
  for serv in serv_list:
    thread.start_new_thread( Threads.fetch_status, (serv_count, 3, serv) )
    thread.start_new_thread( Threads.fetch_cswch, (serv_count, 15, serv) )
    thread.start_new_thread( Threads.generate_table, (serv_count, 0.5, serv) )
    serv_count += 1
except Exception, e:
  print screen.clear + "Application error[subthreadstart]["+serv+"]:", e
  return_code += 1
  Set.Terminal.Cursor.On()
  quit(return_code)
except (SystemExit):
  sys.stdout.write(screen.clear + "SystemExit detected, program stopped.\n")
  sys.stdout.flush()
  return_code += 1
  Set.Terminal.Cursor.On()
  quit(return_code)

# Should be moved to an own classmethod
# Wait for hosts to report in by sleeping
try:  
  spinner = screen.spinning_cursor() # Initiate spinner cusor to spinner, in classmethod  
  while True:
    sys.stdout.write('Warming up host(s): ')
    sys.stdout.write(spinner.next())
    sys.stdout.write(' ' + str(len(arr_status)))
    sys.stdout.write('/' + str(len(serv_list)))
    sys.stdout.flush()
    time.sleep(0.1)
    spin_count += 1 # Used for debugging
    if len(arr_main_table) < len(serv_list):
      sys.stdout.write('\r')
    elif len(arr_main_table) == len(serv_list):
      sys.stdout.write('\rWarming up host(s): done              ')
      sys.stdout.flush()
      time.sleep(0.5)
      arr_main_table.sort()
      sys.stdout.write(screen.clear)
      sys.stdout.flush()
      thread.start_new_thread( screen.print_result() ) # Start printing thread    
      break
except (KeyboardInterrupt):
  Threads.write_to_log_on_exit()
  sys.stdout.write("Program stopped.\n")
  
  sys.stdout.flush()
  Set.Terminal.Cursor.On()
  quit(return_code)
except (SystemExit):
  sys.stdout.write(screen.clear + "Internal error detected, program stopped.\n")
  sys.stdout.flush()
  return_code += 1
  Set.Terminal.Cursor.On()
  quit(return_code)
except Exception, e:
  print screen.clear + "Application error :", e
  return_code += 1
  print 'Program stopped'
  Set.Terminal.Cursor.On()
  quit(return_code)

while 1:
   pass
