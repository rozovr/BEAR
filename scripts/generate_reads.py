#!/usr/bin/python


from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from numpy import random as npr
import sys, csv, StringIO, random, decimal, argparse

complements = {'A':'T', 'C':'G', 'G':'C', 'T':'A',}
def rc_seq(dna):
    rev = reversed(dna)
    return "".join([complements[i] for i in rev])

def get_mod_seq(dna, start, end, limit):
	if start >= limit and end >= limit:
		return dna[(start%limit):(end%limit)]
	elif end >= limit:
		return dna[start:limit] + dna[:(end%limit)]
	else:
		return dna[start:end]

def test_get_mod_seq():
	seq = "AAAAABBBBBCCCCC"
	print seq, len(seq)
	print get_mod_seq(seq,5,10,len(seq))
	print get_mod_seq(seq,20,25,len(seq))
	print get_mod_seq(seq,21,26,len(seq))

# test_get_mod_seq()

parser = argparse.ArgumentParser(description='Generate uniform-length single or paired-end metagenomic reads.')
parser.add_argument('-r', dest="ref", help="Multi-FASTA file containing genomic sequences from which reads will be sampled.")
parser.add_argument('-a', dest="abund", help="Tab-delimited abundance file with an abundance value for each corre- sponding genome sequence in <reference fasta>")
parser.add_argument('-o', dest="output", help="Name for output file containing simulated uniform-length reads")
parser.add_argument('-t', type=int, dest="total", help="The total number of reads to sample from all genomes")
parser.add_argument('-l', type=int, dest="length", help="The length, in bp, of the longest possible read to simulate")
parser.add_argument('-i', type=int, dest="insert", default="0", help="Average length of insert for paired-end reads.")
parser.add_argument('-s', type=int, dest="stddev", default="0", help="Standard deviation of insert length for paired-end reads" )
# parser.add_argument('-d', action='store_true', dest="direction", help="Use this switch to generate reads in both forward and reverse orientations" )
args = parser.parse_args()
 

#Reference metagenome database file (FASTA)
f1 = open(args.ref);

#abundance file (tab-delimited .txt)
f2 = open(args.abund);

total_reads = args.total

max_read_length = args.length
args.direction = True

insert_avg = args.insert
insert_stdev = args.stddev

if(insert_avg):
	f4 = open(args.output + '.1.fasta', 'w')
	f5 = open(args.output + '.2.fasta', 'w')
else:
	f4 = open(args.output, 'w')

frags=[]

div_file = csv.reader(f2, delimiter='\t')
species=[]
diversity=[]

lengths=[]
freqs=[]

for row in div_file:
	species.append(row[0][1:])
	diversity.append(decimal.Decimal(row[1]))

# print "species ", species, len(species)
rand_vec = npr.random(1000000)
ind = 0

for i in SeqIO.parse(f1, 'fasta') :
	genome_num=0	
	while(genome_num < len(species)-1 and not(species[genome_num][:-2] in i.description)) :
		genome_num+=1
	if(species[genome_num][:-2] in i.description) :
		coverage=max(1, int((decimal.Decimal(diversity[genome_num])*total_reads)))
		# limit=len(i.seq)
		# delete foreign characters
		seq = []
		for c in i.seq:
			if c in 'ACGT':
				seq.append(c)
		seq =''.join(seq)
		limit = len(seq)
		for j in range(0, coverage) :
                	# rand = random.random()
                	rand_length = 0
                	numLen = len(lengths)-1
			
			if( (insert_avg != 0) & (insert_stdev != 0)):
				cur_insert = int(random.gauss(insert_avg, insert_stdev))
				if(limit > (max_read_length * 2 + cur_insert)):
					# start1 = random.randint(0, limit-(2*max_read_length + cur_insert))
					# assumes cyclic sequence - keep orig treatment if not
					start1 = random.randint(0,limit-1) # allows pair to overlap cyc at every position
					end1 = start1 + max_read_length
					start2 = end1 + cur_insert
					end2 = start2 + max_read_length
				else:
					start1 = 0
					end1 = limit
					start2 = 0
					end2 = limit


				read1 = get_mod_seq(seq,start1,end1,limit)
				read2 = rc_seq(get_mod_seq(seq,start2,end2,limit))

				if(args.direction):
					# check = random.random()
					check = rand_vec[ind % 1000000]
					ind+=1
					if(check < 0.5): #forward orientation
						f4.write(">%s\n" % i.description)
						f4.write("%s\n" % read1)
						f5.write(">%s\n" % i.description)
                                		f5.write("%s\n" % read2)
					else: #reverse orientation
						f4.write(">%s\n" % i.description)
						f4.write("%s\n" % rc_seq(read1))
						f5.write(">%s\n" % i.description)
						f5.write("%s\n" % rc_seq(read2))
			else:
				if(limit > max_read_length) :	
					start=random.randint(0, limit-max_read_length)
					end=start+max_read_length
				else:
					start=0
					end=limit
				read = i.seq[start:end]
				if(args.direction):
					check = random.random()
					if(check < 0.5): #forward orientation
						f4.write(">%s\n" % i.description)
						f4.write("%s\n" % read)
					else:
						f4.write(">%s\n" % i.description)
						f4.write("%s\n" % read[::-1])
			
	if (genome_num >= len(species) ) :
		break;

f1.close()
f2.close()
f4.close()

