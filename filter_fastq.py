import sys


def gc_count(read):
    count = 0
    for base in read:
        if base == 'C' or base == 'G':
            count += 1
    return count * 100 / len(read)


def valid(read, minlen, gc_bounds):
    if len(read) < minlen:
        return False
    if len(gc_bounds) == 1:
        if gc_count(read) < gc_bounds[0]:
            return False
    elif len(gc_bounds) == 2:
        less = gc_count(read) < gc_bounds[0]
        more = gc_count(read) > gc_bounds[1]
        if less or more:
            return False
    return True


def write_to_file(readlines, file):
    file.write('\n'.join(readlines) + '\n')


MIN_LENGTH = '--min_length'
KEEP_FILTERED = '--keep_filtered'
GC_BOUNDS = '--gc_bounds'
OUTPUT_BASE_NAME = '--output_base_name'

supported_args = [MIN_LENGTH, KEEP_FILTERED, GC_BOUNDS, OUTPUT_BASE_NAME]

splitted = sys.argv[len(sys.argv) - 1].split('.')

min_length = 0
keep_filtered = False
gc_bounds = []
input_file = sys.argv[-1]

output_base_name = '.'.join(splitted[0:len(splitted) - 1])

i = 1
while i < len(sys.argv) - 1:
    if sys.argv[i] not in supported_args:
        raise ValueError('Invalid argument: ' + sys.argv[i])
    if sys.argv[i] == MIN_LENGTH:
        min_length = int(sys.argv[i + 1])
        if min_length <= 0:
            raise ValueError(MIN_LENGTH + ' must be non-negative integer!')
        i += 2
        continue
    if sys.argv[i] == KEEP_FILTERED:
        keep_filtered = True
        i += 1
        continue
    if sys.argv[i] == GC_BOUNDS:
        i += 1
        while sys.argv[i].isnumeric():
            gc_bounds.append(int(sys.argv[i]))
            i += 1
        if len(gc_bounds) > 2:
            raise ValueError(GC_BOUNDS + ' takes maximum 2 values')
        continue
    if sys.argv[i] == OUTPUT_BASE_NAME:
        output_base_name = sys.argv[i + 1]
        i += 2
        continue

fastq_file = open(input_file, 'r')
passed_file = open(output_base_name + '__passed.fastq', 'w')
if keep_filtered:
    failed_file = open(output_base_name + '__failed.fastq', 'w')

all_lines = fastq_file.read().splitlines()

passed = 0
failed = 0
for i in range(0, len(all_lines), 4):
    read_info = all_lines[i:i + 4]
    if i == 0:
        print()
    if valid(read_info[1], min_length, gc_bounds):
        write_to_file(read_info, passed_file)
        passed += 1
    else:
        if keep_filtered:
            write_to_file(read_info, failed_file)
        failed += 1

total_reads = str(len(all_lines) // 4)

print('Done!')
print('Total reads in ' + input_file + ':' + total_reads)
print(str(passed) + ' (' + str(round(passed * 100 / int(total_reads), 2)) + '%) reads passed.')
print(str(failed) + ' (' + str(round(failed * 100 / int(total_reads), 2)) + '%) reads failed.')

passed_file.close()
fastq_file.close()
if keep_filtered:
    failed_file.close()
