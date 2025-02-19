# Importing json library
import json
import sys
def is_number(string):
    if string and (string[0] == '-' or string[0].isdigit()): 
        try:
            float(string) 
            return True
        except ValueError:
            return False
    return False

         

# Opening data.json file
with open("C:/Users/shash/OneDrive/Documents/data.json", 'r', encoding='utf-8') as file:
    # Loading data into a variable "data"
    data = json.load(file)
    
    
# Function to report error
def report_error(line_number, line, expected, received):
    (f"Error in line {line_number}: {line}")
    (f"Expected {expected} tokens, got {received}")

# Function to report invalid register
def report_invalid_register(line_number, line):
    print(f"Error in line {line_number}: {line}")
    print("Invalid register name")
    
# Function to report invalid immediate value
def report_invalid_immediate(line_number, line):
    print(f"Error in line {line_number}: {line}")
    print("Invalid immediate value. Expected integer")

# Function to report invalid range of immediate value
def report_invalid_range(line_number, line, min_val, max_val):
    print(f"Error in line {line_number}: {line}")
    print(f"Invalid value. Expected between {min_val} and {max_val}")
    
# Fundtion to report an undefined label
def report_undefined_label(line_number, line):
    print(f"Error in line {line_number}: {line}")
    print("Undefined label")
     
# Main function to tokenize the elements and find errors in the statements if any
def tokenization(line, data, line_number,labels):
    # Creatung tokens
    tokens = line.replace(",", " ").split()
    # Opcode is the first token
    opcode = tokens[0]
    # Fetching details of instruction formats in the variable "instruction_type"
    instruction_type = data["INSTRUCTION_FORMATS"]
    # R Type Instruction 
    if opcode in instruction_type["R"]:
        # If tokens !=4 : Report Error
        if len(tokens) != 4 :
            report_error(line_number,line,4,len(tokens))
            return None
        # Assigning registers their corresponding values (rd,rs1,rs2)
        if len(tokens) == 4:
           rd, rs1, rs2 = tokens[1], tokens[2], tokens[3]
           # Checking if the register is valid or not 
           if rd not in data["REGISTER_MAP"] or rs1 not in data["REGISTER_MAP"] or rs2 not in data["REGISTER_MAP"]:
               report_invalid_register(line_number, line)
               return None
           # Returning the 32-bit instruction in binary format
           return (
                data["FUNCT7"][opcode] +
                data["REGISTER_MAP"][rs2] +
                data["REGISTER_MAP"][rs1] +
                data["FUNCT3"][opcode] +
                data["REGISTER_MAP"][rd] +
                data["OPCODES"][opcode]   
           )
    # I Type Instruction [1st method]
    elif opcode in instruction_type["I"]:
        # Checking if the opcode is load type or not
        if opcode in data["LOAD_OPCODES"]:
            # If tokens != 3 : Report Error
            if len(tokens)!=3:
                report_error(line,line_number,3,len(tokens))
                return None
            # Assing destination register and (immediate) their corresponding values
            rd,offset=tokens[1],tokens[2]
            # Extracting the immediate value and rs1 from the parenthesis
            if "(" in offset and ")" in offset:
                offset,rs1=offset.split("(")
                rs1=rs1.strip(")")
            else:
                # Print Error if no parenthesis 
                print(f"error in line {line_number}: {line.strip()}")
                print(f"Invalid load instruction format. Expected offset(rs1)")
                return None
            # Print Error if any register is invalid
            if rd not in data["REGISTER_MAP"] or rs1 not in data["REGISTER_MAP"]:
                report_invalid_register(line_number, line)
                return None
            try:
                # Checking if the immediate is integer or not
                offset = int(offset)
            # Print Error : if immediate is not integer 
            except ValueError:
                print(f"Error in line {line_number}: {line}")
                print(f"Invalid offset instruction. Expected integer")
                return None
            min=-2048
            max=2047
            # Print Error : if immediate is not within acceptable range
            if not(-2048<=offset<=2047):
                report_invalid_range(line_number,line,min,max)
                return None
            # 2's complement of offset/immediate
            off=format(offset & 0xFFF,"012b")
            return(
                # Returning the 32-bit binary instruction
                off+data["REGISTER_MAP"][rs1]+data["FUNCT3"][opcode]+data["REGISTER_MAP"][rd]+data["LOAD_OPCODES"][opcode]
            )
        # I Type Instruction [2nd method]
        elif opcode in instruction_type["I"]:
            # Report error if tokens are not 4
            if len(tokens)!=4:
                report_error(line_number, line, 4,len(tokens))
                return None
            # Assign rd, rs1, and immediate their corresponding values
            rd,rs1,imm=tokens[1],tokens[2],tokens[3]
            # Report Error if registers are invalid
            if rd not in data["REGISTER_MAP"] or rs1 not in data["REGISTER_MAP"]:
                report_invalid_register(line_number, line)
                return None
            try:
                # Checking if the immediate is in integer format or not
                imm=int(imm)
            # Report Error if the immediate is not integer type
            except ValueError:              
                print(f"Error in line {line_number}: {line}")
                print(f"Invalid immediate value. Expected integer")
                return None
            min=-2048
            max=2047
            # Report Error if the immediate is not within the acceptable range
            if not(-2048<=imm<=2047):
                report_invalid_range(line_number,line,min,max)
                return None
            # 2's complement of immediate
            imm=format(imm & 0xFFF,"012b")
            # Returning the 32-bit binary instruction
            return (
                imm+data["REGISTER_MAP"][rs1]+
                data["FUNCT3"][opcode]+
                data["REGISTER_MAP"][rd]+
                data["OPCODES"][opcode] 
            )         
    # S Type Instruction   
    elif opcode in instruction_type["S"]:
        # Token list contains [opcode,register1,immediate,register2]
        token=[]
        tokens[2]=tokens[2].replace("("," ").replace(")"," ").split()
        for t in tokens:
            if isinstance(t,list):
                for t1 in t:
                    token.append(t1)
            else:
                token.append(t)
        # If tokens are not 4 : Report Error
        if len(token)!=4:
            print(f"Error in line {line_number}: {line}")
            print(f"Expected 4 tokens, got {len(tokens)} tokens")
            return None
        elif len(token)==4:
            # Assign rd, immediate and rs1 their corresponding values
            rs2=token[1]
            immediate=token[2]
            rs1=token[3]
            # Report Error if any register is invalid
            if rs2 not in data["REGISTER_MAP"] or rs1 not in data["REGISTER_MAP"]:
                print(f"Error in line {line_number}: {line}")
                print("Invalid register name")
                return None
            try:
                # Checking if the immediate is integer type or not
                immediate=int(immediate)
            # Report Error if the immediate is not integer
            except ValueError:
                print(f"Error in line {line_number}: {line}")
                print(f"Invalid immediate value. Expected integer")
            
            if isinstance(immediate,int):
                # Return the 32-bit binary instruction
                if immediate>=-2048 and immediate<=2047:
                    immediate=format(immediate & 0xFFF, "012b")
                    return (immediate[0:7]+data["REGISTER_MAP"][rs2]+data["REGISTER_MAP"][rs1]+data["FUNCT3"][opcode]+immediate[7:12]+data["OPCODES"][opcode])
                # Report Error if the immediate is not within the acceptable range 
                else:
                    print(f"Error in line {line_number}: {line}")
                    print(f"Invalid immediate value. Expected value between -2048 and 2047")
            # Report Error if immediate is not integer
            else:
                print(f"Error in line {line_number}: {line}")
                print(f"Invalid immediate value. Expected integer")
    # B Type Instruction
    elif opcode in instruction_type["B"]:
        # Report Error if tokens are not 4
        if len(tokens)!=4:
            report_error(line_number,line,4,len(tokens))
            return None
        # Assigning registers and label their corresponding values
        rs1,rs2,label=tokens[1],tokens[2],tokens[3]
        # Report Error if the registers are invalid
        
        
        
        
        if rs1 not in data["REGISTER_MAP"] or rs2 not in data["REGISTER_MAP"]:
            report_invalid_register(line_number,line)
            return None
        
        
        
        if is_number(label):
            label=int(label)
            offset=label//2
            
            if label%4!=0:
                print("the third token is expected to be a divisible of 2")
                return None
        else:
            if label not in labels:
                report_undefined_label(line_number,line)
                return None
            
                
                
                
        # Report error if the label is undefined
        # if label not in labels:
        #     report_undefined_label(line_number,line)
        #     return None
        
        
        # Finding line of label
            star_line=labels[label]
        # Finding equivalent immediate value
            offset=(star_line-line_number)*2
        # Report Error if the immediate is not within the acceptable range
        if offset<=-2048 and offset>=2047:
            report_invalid_range(line_number,line,-2048,2047)
            return None
        # 2's complement of offset
        offset=format(offset & 0xFFF, "012b")
        # Returning the 32-bit binary instruction
        return (
            offset[0] + offset[2:8] +  
            data["REGISTER_MAP"][rs2] + 
            data["REGISTER_MAP"][rs1] + 
            data["FUNCT3"][opcode] + 
            offset[8:12] + offset[1] +  
            data["OPCODES"][opcode]
        )
    # J Type instruction
    elif opcode in instruction_type["J"]:
        # Report Error if the tokens are not 3
        if len(tokens)!=3:
            print(f"Error in line {line_number}: {line}")
            print(f"Expected 3 tokens, got {len(tokens)} tokens")
            return None
        elif len(tokens)==3:
            # Assigning register and immediate their corresponding values
            rd=tokens[1]
            immediate=tokens[2]
            # Report Error if the register is invalid
            if rd not in data["REGISTER_MAP"]:
                print(f"Error in line {line_number}: {line}")
                print("Invalid register name")
                return None
            # try:
            #     # Checking if the offset is of integer type or not
            #     immediate=int(immediate)
            if is_number(immediate):
                immediate=int(immediate)
                if immediate%4!=0:
                    return None
            else:
                if immediate not in labels:
                    report_undefined_label(line_number,line)
                    return None
                star_line=labels[immediate]
                immediate=(star_line-line_number)*4
                # Report Error if the immediate is not within the acceptable range
                
                
                
                
            # Report Error if the immediate is not integer
            # except ValueError:
            #     print(f"Error in line {line_number}: {line}")
            #     print(f"Invalid immediate value. Expected integer")
            #     return None
            if isinstance(immediate,int):
                # Return the 32-bit binary instruction if the immediate is in acceptable range otherwise print error
                if immediate>=-1048576 and immediate<=1048575:
                    imm=format(immediate & 0xFFFFFFFF,"032b")
                    return (imm[11]+imm[21:31]+imm[20]+imm[12:20]+data["REGISTER_MAP"][rd]+data["OPCODES"][opcode])
                else:
                    print(f"Error in line {line_number}: {line}")
                    print(f"Invalid immediate value. Expected value between -1048576 and 1048575")
    # Report Error if the instruction is other than R,I,S,B,J
    else:
        print(f"This instruction is not supported. Kindly try again.")

# Reading the input.txt file and writing the output in output.txt file
input_file=sys.argv[-2]
output_file=sys.argv[-1]
with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    labels={}
    line_number = 1
    for line in infile:
        line = line.strip()
        if not line or line.startswith('#'):
            line_number+=1
            continue
        if ":" in line:
            label=line.split(":")[0].strip()
            labels[label]=line_number
        line_number+=1
    infile.seek(0)   
    line_number=1
    
    for line in infile:
        if not line or line.startswith("#"): 
            line_number+= 1
            continue
        if ":" in line:
            parts = line.split(":")
            line=parts[1].strip()       
        binary_code = tokenization(line, data, line_number,labels)
        if binary_code:
            outfile.write(binary_code + "\n")
        elif not binary_code:
            print(f"Error in line {line_number}: {line}")
            outfile.write(f"Error in line {line_number}: {line} Skipping..\n")
        line_number += 1
        
    
print(f"Binary instructions written to output.txt")
