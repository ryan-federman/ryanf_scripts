# create movable soft deformer
import maya.cmds as cmds
import copy


def soft_deformer(ctrl_name, switch=False):
    # get position for the follicle on the mesh
    selection = cmds.ls(sl=True)
    geo = selection[0].split('.')[0]
    component = selection[0].split('.')[1]
    pos_x = 0
    pos_y = 0
    uvs = []

    # check to see if you need to convert
    if 'f' in component:
        uvs = cmds.polyListComponentConversion(ff=True, tuv=True)

    elif 'map' in component:
        uvs = copy.deepcopy(selection)

    else:
        cmds.error('Select a face or uv coordinates')

    # account for unflattened lists of uvs, change to a flattened list
    uv_list = []
    for each in uvs:
        if ':' in each:
            each = each.split('[')[1].split(']')[0]
            nums = each.split(':')
            difference = int(nums[1]) - int(nums[0])
            # add already existing uvs into the list
            for num in nums:
                uv = geo + '.map[{}]'.format(num)
                uv_list.append(uv)
            if difference > 1:
                for x in range(1, difference):
                    mid_uv = geo + '.map[{}]'.format(str(int(nums[1]) - x))
                    uv_list.append(mid_uv)
        else:
            uv_list.append(each)

    # get average position in uv space of all coordinates
    uv_pos_x = []
    uv_pos_y = []
    x = 0
    y = 0
    for each in uv_list:
        uv_pos = cmds.polyEditUV(each, query=True)
        uv_pos_x.append(uv_pos[0])
        uv_pos_y.append(uv_pos[1])
    for each in uv_pos_x:
        x = x + each
    for each in uv_pos_y:
        y = y + each
    pos_x = x/len(uv_list)
    pos_y = y/len(uv_list)

    # create follicle
    foll = cmds.createNode('follicle', name=ctrl_name + '_follicle')
    foll_transform = cmds.listRelatives(foll, parent=True)[0]
    foll_transform = cmds.rename(foll_transform, foll + '_srt')

    geo_shape = cmds.listRelatives(geo, s=True)[0]
    cmds.connectAttr(geo_shape + '.outMesh', foll + '.inputMesh')
    cmds.connectAttr(geo_shape + '.worldMatrix[0]', foll + '.inputWorldMatrix')
    cmds.setAttr(foll + '.parameterU', pos_x)
    cmds.setAttr(foll + '.parameterV', pos_y)

    cmds.connectAttr(foll + '.outTranslate', foll_transform + '.translate')
    cmds.connectAttr(foll + '.outRotate', foll_transform + '.rotate')
