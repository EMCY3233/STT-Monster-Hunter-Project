"""Conservative A32 PC-literal + straight-line constant-address candidates.

Static pattern candidates only: instruction state/reachability/execution unverified.
No pointer dereferencing or runtime writes. Capstone 5.0.6 required.
"""
import argparse,hashlib,json,struct,sys
from pathlib import Path


def scan(image, segments, targets, capstone, thumb=False):
    from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM, ARM_CC_AL, ARM_INS_LDR, ARM_INS_STR, ARM_INS_MOV, ARM_INS_ADD, ARM_INS_SUB
    md=capstone.Cs(capstone.CS_ARCH_ARM,(capstone.CS_MODE_THUMB if thumb else capstone.CS_MODE_ARM)|capstone.CS_MODE_LITTLE_ENDIAN);md.detail=True
    text=next(s for s in segments if s['name']=='text');base=text['address'];off=text['file_offset'];size=text['code_bytes']
    def mapped(va,n):
        for s in segments:
            delta=va-s['address']
            if 0<=delta and delta+n<=s['code_bytes']:
                return s['file_offset']+delta
        return None
    found=[];literals=0
    for relative in range(0,size-(1 if thumb else 3),2 if thumb else 4):
        address=base+relative
        if thumb:
            word=struct.unpack_from('<H',image,off+relative)[0]
            if word&0xf800!=0x4800:continue
            literal=((address+4)&~3)+(word&255)*4
        else:
            word=struct.unpack_from('<I',image,off+relative)[0]
            # AL-only, immediate PC-relative LDR word, preindexed, no writeback.
            if word>>28!=14 or word&0x0f7f0000!=0x051f0000:continue
            literal=address+8+(1 if word&(1<<23) else -1)*(word&4095)
        literal_offset=mapped(literal,4)
        if literal_offset is None:continue
        value=struct.unpack_from('<I',image,literal_offset)[0]
        if not any(abs(t-value)<=4095 for t in targets):continue
        width=2 if thumb else 4
        decoded=list(md.disasm(image[off+relative:off+relative+width],address))
        if len(decoded)!=1 or decoded[0].id!=ARM_INS_LDR:continue
        seed=decoded[0];reg=seed.operands[0].reg
        known={reg:value};literals+=1;trace=[dict(address=address,mnemonic=seed.mnemonic,operands=seed.op_str)]
        following=image[off+relative+width:off+min(size,relative+width+80)]
        for ins in md.disasm(following,address+width):
            trace.append(dict(address=ins.address,mnemonic=ins.mnemonic,operands=ins.op_str))
            if ins.cc!=ARM_CC_AL or any(ins.group(g) for g in (capstone.CS_GRP_JUMP,capstone.CS_GRP_CALL,capstone.CS_GRP_RET,capstone.CS_GRP_INT)):
                break
            ops=ins.operands;new=None
            if ins.id in (ARM_INS_LDR,ARM_INS_STR) and len(ops)==2 and ops[1].type==ARM_OP_MEM:
                mem=ops[1].mem
                if mem.base in known and not mem.index and not ins.writeback:
                    target=(known[mem.base]+mem.disp)&0xffffffff
                    if target in targets:
                        found.append(dict(seed_address=address,literal_address=literal,literal_value=value,
                            instruction_address=ins.address,target_address=target,
                            access='read' if ins.id==ARM_INS_LDR else 'write',
                            base_register=ins.reg_name(mem.base),displacement=mem.disp,
                            trace=list(trace),runtime_execution_verified=False,instruction_state_verified=False))
            if ins.id==ARM_INS_MOV and len(ops)==2 and ops[0].type==ARM_OP_REG:
                if ops[1].type==ARM_OP_REG and ops[1].reg in known and not ops[1].shift.type:new=(ops[0].reg,known[ops[1].reg])
            if ins.id in (ARM_INS_ADD,ARM_INS_SUB) and len(ops)==3 and ops[0].type==ARM_OP_REG and ops[1].type==ARM_OP_REG and ops[2].type==ARM_OP_IMM and ops[1].reg in known:
                new=(ops[0].reg,(known[ops[1].reg]+(1 if ins.id==ARM_INS_ADD else -1)*ops[2].imm)&0xffffffff)
            _,writes=ins.regs_access()
            for r in writes:known.pop(r,None)
            if new is not None:known[new[0]]=new[1]
            if capstone.arm.ARM_REG_PC in writes or not known:break
    return dict(method=('T16' if thumb else 'AL A32')+' PC-relative literal seed plus <=80 following bytes; no branches followed',
                candidate_seeds=literals,access_candidates=found,instruction_state_verified=False,
                runtime_execution_verified=False,absence_does_not_prove_no_references=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',type=Path,required=True);p.add_argument('--mapping',type=Path,required=True)
    p.add_argument('--capstone-path',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--targets',nargs='+',type=lambda x:int(x,0),required=True)
    p.add_argument('--thumb',action='store_true')
    a=p.parse_args();sys.path.insert(0,str(a.capstone_path));import capstone
    if capstone.__version__!='5.0.6':raise ValueError('requires pinned Capstone 5.0.6')
    image=a.image.read_bytes();mapping=json.loads(a.mapping.read_bytes());digest=hashlib.sha256(image).hexdigest()
    if digest!=mapping['output_sha256'] or len(image)!=mapping['output_bytes']:raise ValueError('static image identity mismatch')
    if a.out.exists():raise ValueError('new output file required')
    result=scan(image,mapping['segments'],a.targets,capstone,a.thumb)
    result.update(image_sha256=digest,capstone_version=capstone.__version__,targets=a.targets)
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(candidate_seeds=result['candidate_seeds'],access_candidates=len(result['access_candidates']),reads=sum(x['access']=='read' for x in result['access_candidates']),writes=sum(x['access']=='write' for x in result['access_candidates']))))
