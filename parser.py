import functions as f

def parser(cmd):
    cmd = f.expand_globs(cmd)

    cmd_segmented=[]
    current_segment=[]
    operations = []
    for token in cmd:
        if token == "&&":
            cmd_segmented.append(current_segment)
            operations.append("&&")
            current_segment=[]
        elif token == "||":
            cmd_segmented.append(current_segment)
            operations.append("||")
            current_segment=[]
        else:
            current_segment.append(token)
    cmd_segmented.append(current_segment)

    current_stage=[]
    cmd_staged=[]
    for segment in cmd_segmented:
        current_stage=[]
        stages=[]
        for token in segment:
            if token != "|":
                current_stage.append(token)
            else:
                stages.append(current_stage)
                current_stage=[]
        stages.append(current_stage)
        cmd_staged.append(stages)

    parsed_cmd = []
    for segment in cmd_staged:
        segment_result = []
        for stage in segment:
            piece = []
            redirects = []
            for i, token in enumerate(stage):
                if token == ">":
                    redirects.append((">", stage[i+1]))
                    break
                elif token == ">>":
                    redirects.append((">>", stage[i+1]))
                    break
                elif token == "<":
                    redirects.append(("<", stage[i+1]))
                    break
                else:
                    piece.append(token)
            segment_result.append([piece, redirects])
        parsed_cmd.append(segment_result)
    return parsed_cmd, operations
