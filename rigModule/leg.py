from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/legWidgetOptions.ui'


class LegWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(LegWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['LegIk', 'LegPv', 'UpLeg', 'Knee', 'Foot', 'Toe']
        self.initiateMayaNodes(self.controlers)
        # 		self.shapes = {}

        '''
        self.controlName
        self.grpOffsets
        self.joints
        self.sknJnts
        '''

    def addData(self):
        '''
        It's where you define controle shapes, grpOffset and skinning joint.
        You need to add them to the node info to be able to use them before it's actually rigged.
        It's only called when the node is created the first time.
        '''

        # add two other grpOffsets to the Global and 1 more sknJnts to the Cog
        # 		self.addGrpOffset(self.controlers[0], name = 'default')
        # 		self.addGrpOffset(self.controlers[0], name = 'default')
        # 		self.addSknJnt(self.controlers[3], name = 'specialSkTest_sknJnt')

        # 		self.addJoint(self.controlers[3])
        # 		self.addSknJnt(self.controlers[3])

        # set here default value for the controlers and shape.
        self.setControlerShape('LegIk', 'cube', 7, axe='x')
        self.setControlerShape('LegPv', 'cube', 7, axe='x', radius=0.2)
        self.setControlerShape('UpLeg', 'sphere', 14, axe='x')
        self.setControlerShape('Knee', 'circle', 14, axe='x')
        self.setControlerShape('Foot', 'circle', 14, axe='x')
        self.setControlerShape('Toe', 'circle', 14, axe='x')

        # add knee option to the templateGrp
        cmds.addAttr(self.templateGrp, ln='doubleKnee', at='bool')
        cmds.setAttr(self.templateGrp + '.doubleKnee', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='numTwist', at='long')
        cmds.setAttr(self.templateGrp + '.numTwist', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

    def updateKnee(self, state):
        node = self.getNode()
        if state:
            # create jnt and parent it
            name = '{}_{}_template'.format(node, '2bis')
            jnt = cmds.createNode('joint', n=name, p=self.templateControlers[1])
            cmds.setAttr(jnt + '.radius', cmds.getAttr(self.templateControlers[1] + '.radius'))
            pos = cmds.getAttr(self.templateControlers[2] + '.t')[0]
            cmds.setAttr(jnt + '.t', pos[0] / 5, pos[1] / 5, 0)
            self.templateControlers.insert(2, jnt)
            cmds.parent(self.templateControlers[3], jnt)
            cmds.setAttr(self.templateGrp + '.doubleKnee', True)

        else:
            # reparent the jnt and delete the doubleKnee
            if len(self.templateControlers) == 9:
                cmds.parent(self.templateControlers[3], self.templateControlers[1])
                cmds.delete(self.templateControlers[2])
                self.templateControlers.pop(2)
                cmds.setAttr(self.templateGrp + '.doubleKnee', False)

        cmds.setAttr(self.templateGrp + '.isTemplate', str(self.templateControlers), type='string')
        cmds.select(self.templateGrp)

        if cmds.objExists('{}_TEMP_sknJnt_grp'.format(node)):
            cmds.delete('{}_TEMP_sknJnt_grp'.format(node))

        self.setState(1)

    def updateNumTwist(self, value):
        cmds.setAttr(self.templateGrp + '.numTwist', value)
        self.setState(1)

    def options(self):
        super(LegWidget, self).options()
        # this happen after the item and the node are created.
        if cmds.objExists(self.templateGrp):
            if not cmds.objExists(self.templateGrp + '.doubleKnee'):
                cmds.addAttr(self.templateGrp, ln='doubleKnee', at='bool')
                cmds.setAttr(self.templateGrp + '.doubleKnee', e=True, keyable=True)
            if not cmds.objExists(self.templateGrp + '.numTwist'):
                cmds.addAttr(self.templateGrp, ln='numTwist', at='long')
                cmds.setAttr(self.templateGrp + '.numTwist', e=True, keyable=True)

            isDoubleKnee = cmds.getAttr(self.templateGrp + '.doubleKnee')
            self.qtOptions.doubleKnee_ckb.setChecked(isDoubleKnee)
            numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
            self.qtOptions.numTwist_box.setValue(numTwist)

            if not cmds.objExists(self.templateGrp + '.prependName'):
                cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
                cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
            prependName = cmds.getAttr(self.templateGrp + '.prependName')
            self.prependName_chbx.setChecked(prependName)

            if not cmds.objExists(self.templateGrp + '.prependNameTxt'):
                cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
                cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)
            prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
            self.prependName_lineEdit.setText(prependNameTxt)

        self.qtOptions.doubleKnee_ckb.stateChanged.connect(partial(self.updateKnee))
        self.qtOptions.numTwist_box.valueChanged.connect(partial(self.updateNumTwist))
        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None] * 8
        pos = [(0, 9, 0), (0, 5, 0.25), (0, 0.5, 0), (0, 0, 1.5), (0, 0, 2.5), (0, 0, -0.5), (-0.5, 0, 1.5),
               (0.5, 0, 1.5)]
        for i in range(8):
            name = '{}_{}_template'.format(node, str(i + 1))
            if cmds.objExists(name):
                self.templateControlers[i] = name
            else:
                self.templateControlers[i] = cmds.createNode('joint', n=name, p=self.templateGrp)

                cmds.setAttr(self.templateControlers[i] + '.t', pos[i][0], pos[i][1], pos[i][2])
                if i == 5:
                    self.templateControlers[i] = cmds.parent(self.templateControlers[i], self.templateControlers[2])[0]
                elif i == 7 or i == 6:
                    self.templateControlers[i] = cmds.parent(self.templateControlers[i], self.templateControlers[3])[0]
                elif i:
                    self.templateControlers[i] = \
                    cmds.parent(self.templateControlers[i], self.templateControlers[i - 1])[0]
            cmds.setAttr(self.templateControlers[i] + '.radius', 0.5)

    # cmds.select(ik[0])

    def defaultWidget(self):
        pass

    def rig(self):
        ''' well ...
        TODO > add joint for foot side,
        '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        radius = 1
        isDoubleKnee = cmds.getAttr(self.templateGrp + '.doubleKnee')
        numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt

        # positions from template transforms/joints
        count = 8
        if isDoubleKnee:
            count += 1

        positions = [None] * count
        for i in range(count):
            positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)

        #
        # joints, part 1
        #
        count = 5
        if isDoubleKnee:
            count += 1

        ik = [None] * count
        for i in range(count):
            ik[i] = cmds.createNode('joint', n=node + '_ik' + str(i + 1))
            cmds.setAttr(ik[i] + '.t', positions[i][0], positions[i][1], positions[i][2])

        if positions[0][0] >= -0.001:
            cmds.delete(cmds.aimConstraint(ik[1], ik[0], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[2]))
            cmds.delete(cmds.aimConstraint(ik[2], ik[1], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[0]))
            cmds.delete(cmds.aimConstraint(ik[-2], ik[-3], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[1]))
            cmds.delete(cmds.aimConstraint(ik[-1], ik[-2], aim=(1, 0, 0), u=(0, 0, 1), wut='scene'))
            cmds.delete(cmds.aimConstraint(ik[-2], ik[-1], aim=(-1, 0, 0), u=(0, 0, 1), wut='scene'))
            if isDoubleKnee:
                cmds.delete(cmds.aimConstraint(ik[3], ik[2], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[0]))

        else:
            cmds.delete(cmds.aimConstraint(ik[1], ik[0], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[2]))
            cmds.delete(cmds.aimConstraint(ik[2], ik[1], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[0]))
            cmds.delete(cmds.aimConstraint(ik[-2], ik[-3], aim=(-1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[1]))
            cmds.delete(cmds.aimConstraint(ik[-1], ik[-2], aim=(-1, 0, 0), u=(0, 0, -1), wut='scene'))
            cmds.delete(cmds.aimConstraint(ik[-2], ik[-1], aim=(1, 0, 0), u=(0, 0, -1), wut='scene'))
            if isDoubleKnee:
                cmds.delete(cmds.aimConstraint(ik[3], ik[2], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[0]))

        for i in range(count):
            r = cmds.getAttr(ik[i] + '.r')[0]
            cmds.setAttr(ik[i] + '.jo', r[0], r[1], r[2])
            cmds.setAttr(ik[i] + '.r', 0, 0, 0)
            cmds.setAttr(ik[i] + '.radius', radius * 0.5)

        ik_ctrl_grp = [None] * 2
        ik_ctrl = [None] * 2
        ctrlInfo = self.getInfoControl(self.controlers[0])

        ik_ctrl_grp[0], ik_ctrl[0] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                      color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                      axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                      position=ik[-3], node=node, \
                                                      lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])

        # 		cmds.addAttr(ik_ctrl[0], ln='joints', at='bool', dv=True, k=True)
        # 		cmds.addAttr(ik_ctrl[0], ln='editJoints', at='bool', k=True)
        cmds.addAttr(ik_ctrl[0], ln='fkControls', at='bool', dv=True, k=True)
        cmds.addAttr(ik_ctrl[0], ln='ikControls', at='bool', dv=True, k=True)
        cmds.addAttr(ik_ctrl[0], ln='stretch', at='bool', k=True)
        cmds.addAttr(ik_ctrl[0], ln='footRoll', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='footSide', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='heelTwist', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='ballLift', at='double', k=True)
        # cmds.addAttr(ik_ctrl[0], ln='toeLift', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='toeTwist', at='double', k=True)

        heel = cmds.createNode('transform', n=node + '_heel_grp')
        cmds.setAttr(heel + '.t', positions[-3][0], positions[-3][1], positions[-3][2])
        heel = cmds.parent(heel, ik_ctrl[0])[0]
        cmds.setAttr(heel + '.r', 0, 0, 0)
        cmds.connectAttr(ik_ctrl[0] + '.footRoll', heel + '.rx')
        cmds.connectAttr(ik_ctrl[0] + '.heelTwist', heel + '.ry')
        cmds.transformLimits(heel, rx=(0, 0), erx=(False, True))
        cmds.hide(heel)

        side_rt = cmds.createNode('transform', n=node + '_side_rt_grp', p=heel)
        cmds.setAttr(side_rt + '.r', 0, 0, 0)
        cmds.move(positions[-2][0], positions[-2][1], positions[-2][2], side_rt, ws=True)

        if positions[0][0] <= -0.001:
            rev = cmds.createNode('reverse')
            cmds.connectAttr(ik_ctrl[0] + '.footSide', rev + '.inputX')
            cmds.connectAttr(rev + '.outputX', side_rt + '.rz')
            cmds.transformLimits(side_rt, rz=(0, 0), erz=(False, True))
        else:
            cmds.connectAttr(ik_ctrl[0] + '.footSide', side_rt + '.rz')
            cmds.transformLimits(side_rt, rz=(0, 0), erz=(True, False))

        side_lf = cmds.createNode('transform', n=node + '_side_lf_grp', p=side_rt)
        cmds.setAttr(side_lf + '.r', 0, 0, 0)
        cmds.move(positions[-1][0], positions[-1][1], positions[-1][2], side_lf, ws=True)

        if positions[0][0] <= -0.001:
            cmds.connectAttr(ik_ctrl[0] + '.footSide', rev + '.inputY')
            cmds.connectAttr(rev + '.outputY', side_lf + '.rz')
            cmds.transformLimits(side_lf, rz=(0, 0), erz=(True, False))
        else:
            cmds.connectAttr(ik_ctrl[0] + '.footSide', side_lf + '.rz')
            cmds.transformLimits(side_lf, rz=(0, 0), erz=(False, True))

        toe = cmds.createNode('transform', n=node + '_toe_grp', p=side_lf)
        cmds.delete(cmds.pointConstraint(ik[-1], toe))
        cmds.setAttr(toe + '.r', 0, 0, 0)
        cmds.connectAttr(ik_ctrl[0] + '.toeTwist', toe + '.ry')
        cmds.setDrivenKeyframe(toe + '.rx', v=0, dv=45, cd=ik_ctrl[0] + '.footRoll', itt='linear', ott='linear')
        cmds.setDrivenKeyframe(toe + '.rx', v=45, dv=90, cd=ik_ctrl[0] + '.footRoll', itt='linear', ott='linear')

        curveDrivenKey = cmds.listConnections(toe + '.rotateX')[0]
        cmds.selectKey(curveDrivenKey)
        cmds.setInfinity(poi='cycleRelative')

        ball = cmds.createNode('transform', n=node + '_ball_grp', p=toe)
        cmds.delete(cmds.pointConstraint(ik[-2], ball))
        cmds.setAttr(ball + '.r', 0, 0, 0)
        cmds.connectAttr(ik_ctrl[0] + '.ballLift', ball + '.rax')
        cmds.setDrivenKeyframe(ball + '.rx', v=0, dv=0, cd=ik_ctrl[0] + '.footRoll', itt='linear', ott='linear')
        cmds.setDrivenKeyframe(ball + '.rx', v=45, dv=45, cd=ik_ctrl[0] + '.footRoll', itt='linear', ott='linear')
        cmds.setDrivenKeyframe(ball + '.rx', v=0, dv=90, cd=ik_ctrl[0] + '.footRoll', itt='linear', ott='linear')

        ctrlInfo = self.getInfoControl(self.controlers[1])
        ik_ctrl_grp[1], ik_ctrl[1] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                      color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                      axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                      position=ik[1], rotation=ik[1], node=node, \
                                                      lockAttr=['r', 's'],
                                                      hideAttr=['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

        distance = rigUtils.getDistance(ik[1], ik[-2])
        if positions[0][0] <= -0.001:
            cmds.move(0, 0, distance * (-0.9), ik_ctrl_grp[1], os=True, r=True, wd=True)
        else:
            cmds.move(0, 0, distance * (0.9), ik_ctrl_grp[1], os=True, r=True, wd=True)
        cmds.setAttr(ik_ctrl_grp[1] + '.r', 0, 0, 0)
        cmds.connectAttr(ik_ctrl[0] + '.ikControls', ik_ctrl_grp[1] + '.v')

        #
        # ik stretch joints
        #

        count = 3
        if isDoubleKnee:
            count += 1

        ik2 = [None] * (count)
        for i in range(count):
            ik2[i] = cmds.duplicate(ik[i])[0]
            ik2[i] = cmds.rename(ik2[i], node + '_ik' + str(i + 1) + '_str')
            if i == 0:
                ik2[i] = cmds.parent(ik2[i], self.rigGrp)[0]
            else:
                ik2[i] = cmds.parent(ik2[i], ik2[i - 1])[0]
            c = cmds.parentConstraint(ik[i], ik2[i])[0]
            cmds.rename(c, node + '_ik' + str(i + 1) + '_parcon')
            cmds.setAttr(ik2[i] + '.jo', 0, 0, 0)

        count = 4
        if isDoubleKnee:
            count += 1

        fk_ctrl = [None] * count
        fk_ctrl_grp = [None] * count
        jnt = [None] * count
        sknJnt = [None] * count
        for i in range(count):
            o = i
            sub = ''
            if count == 5:
                if i == 2:
                    o = 1
                    sub = 'Bis'
                if i > 2:
                    o = i - 1

            ctrlInfo = self.getInfoControl(self.controlers[o + 2])
            fk_ctrl_grp[i], fk_ctrl[i] = rigUtils.control(name=preName + ctrlInfo[0] + sub, side=ctrlInfo[1],
                                                          shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                          radius=ctrlInfo[7], \
                                                          axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                          parent=self.rigGrp, position=ik[i], rotation=ik[i], node=node, \
                                                          lockAttr=['s'],
                                                          hideAttr=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'],
                                                          controlType='joint')

            if i != count - 1:
                cmds.connectAttr(ik2[i] + '.t', fk_ctrl_grp[i] + '.t')
                cmds.connectAttr(ik2[i] + '.r', fk_ctrl_grp[i] + '.jo')
            else:
                cmds.connectAttr(ik[i] + '.t', fk_ctrl_grp[i] + '.t')
                cmds.connectAttr(ik[i] + '.jo', fk_ctrl_grp[i] + '.jo')
            cmds.setAttr(fk_ctrl_grp[i] + '.r', 0, 0, 0)

            if cmds.listRelatives(fk_ctrl[i], pa=True, s=True):
                cmds.connectAttr(ik_ctrl[0] + '.fkControls', cmds.listRelatives(fk_ctrl[i], pa=True, s=True)[0] + '.v')

            if i:
                fk_ctrl_grp[i] = cmds.parent(fk_ctrl_grp[i], fk_ctrl[i - 1])[0]
                # now let's find his real ctrl in case we have several module with the same name
                obj = cmds.listRelatives(fk_ctrl_grp[i], ad=True, type='transform')[::-1][len(ctrlInfo[6])]
                allObj = cmds.ls(obj)
                if len(allObj) > 1:
                    for ctrl in allObj:
                        if fk_ctrl_grp[i] in ctrl:
                            fk_ctrl[i] = ctrl
                            break
                else:
                    fk_ctrl[i] = obj

            # 			else: fk_ctrl_grp[i] = cmds.parent(fk_ctrl_grp[i], self.rigGrp)[0]
            # 			cmds.setAttr(fk_ctrl[i]+'.drawStyle', 2)

            side = ''
            if ctrlInfo[1] != 'None':
                side = ctrlInfo[1] + '_'

            # fk joints
            jnt[i] = cmds.duplicate(ik[i])[0]
            jnt[i] = cmds.parent(jnt[i], fk_ctrl[i])[0]
            jnt[i] = cmds.rename(jnt[i], '{}{}{}{}_0_jnt'.format(side, preName, self.controlers[o + 2], sub))
            sknJnt[i] = rigUtils.joint(position=ik[i], orientation=ik[i],
                                       name='{}{}{}_0_sknJnt'.format(preName, self.controlers[o + 2], sub),
                                       parent=jnt[i], node=node, side=ctrlInfo[1])
            for a in ['t', 'r', 'jo']: cmds.setAttr(jnt[i] + '.' + a, 0, 0, 0)
            cmds.setAttr(sknJnt[i] + '.radius', 0.35)
            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v')
            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.setAttr(fk_ctrl[i] + '.drawStyle', 2)

        # finish foot roll
        cmds.setDrivenKeyframe(fk_ctrl[-1] + '.jointOrientY', v=0, dv=0, cd=ik_ctrl[0] + '.footRoll', itt='linear',
                               ott='linear')
        cmds.setDrivenKeyframe(fk_ctrl[-1] + '.jointOrientY', v=-45, dv=45, cd=ik_ctrl[0] + '.footRoll', itt='linear',
                               ott='linear')
        cmds.setDrivenKeyframe(fk_ctrl[-1] + '.jointOrientY', v=0, dv=90, cd=ik_ctrl[0] + '.footRoll', itt='linear',
                               ott='linear')

        rev = cmds.createNode('reverse')
        cmds.connectAttr(ik_ctrl[0] + '.ballLift', rev + '.inputX')
        cmds.connectAttr(rev + '.outputX', jnt[-1] + '.ry')

        for i in range(1, count + 1):
            ik[i] = cmds.parent(ik[i], ik[i - 1])[0]
        cmds.select(ik);
        cmds.SetPreferredAngle()

        rigUtils.ikHandle(node + '_ball', ik[-3], ik[-2], parent=ball)
        rigUtils.ikHandle(node + '_toe', ik[-2], ik[-1], parent=toe)
        ikh = rigUtils.ikHandle(node, ik[0], ik[-3], parent=ball)[0]
        pvc = cmds.poleVectorConstraint(ik_ctrl[1], ikh)[0]
        cmds.rename(pvc, node + '_pvcon')

        #
        # stretch math
        #

        ik1_jnt_grp = cmds.createNode('transform', n=ik[0] + '_grp', p=self.rigGrp)
        cmds.delete(cmds.pointConstraint(ik[0], ik1_jnt_grp))
        n = cmds.duplicate(ik1_jnt_grp)[0]
        n = cmds.rename(n, 'str_grp')
        db1 = cmds.createNode('distanceBetween')
        cmds.connectAttr(ik1_jnt_grp + '.worldMatrix', db1 + '.inMatrix1')
        cmds.connectAttr(ik_ctrl[0] + '.worldMatrix', db1 + '.inMatrix2')
        db2 = cmds.createNode('distanceBetween')
        cmds.connectAttr(n + '.worldMatrix', db2 + '.inMatrix1')
        cmds.connectAttr(ik_ctrl_grp[0] + '.worldMatrix', db2 + '.inMatrix2')
        md1 = cmds.createNode('multiplyDivide')
        cmds.setAttr(md1 + '.operation', 2)
        cmds.connectAttr(db1 + '.distance', md1 + '.input1X')
        cmds.connectAttr(db2 + '.distance', md1 + '.input2X')
        md2 = cmds.createNode('multiplyDivide')
        cmds.connectAttr(md1 + '.outputX', md2 + '.input1X')
        cmds.connectAttr(ik_ctrl[0] + '.stretch', md2 + '.input2X')
        c = cmds.createNode('condition')
        cmds.setAttr(c + '.secondTerm', 1)
        cmds.setAttr(c + '.operation', 3)
        cmds.connectAttr(md1 + '.outputX', c + '.colorIfTrueR')
        cmds.connectAttr(md2 + '.outputX', c + '.firstTerm')

        cmds.connectAttr(c + '.outColorR', ik[0] + '.sx')
        cmds.connectAttr(c + '.outColorR', ik[1] + '.sx')

        cmds.parentConstraint(ik_ctrl[0], ik_ctrl_grp[1], mo=True)

        #
        # lock and hide attributes
        #

        for i in range(count):
            o = i
            if isDoubleKnee:
                o = i - 1
            if i == 0 or o == 2:
                for a in ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius']:
                    cmds.setAttr(fk_ctrl[i] + '.' + a, l=True, k=False, cb=False)
            else:
                for a in ['tx', 'ty', 'tz', 'rx', 'rz', 'sx', 'sy', 'sz', 'v', 'radius']:
                    cmds.setAttr(fk_ctrl[i] + '.' + a, l=True, k=False, cb=False)

        # selection sets
        # 		common.sets(name, jnt, fk_ctrl, ik_ctrl)

        # fk to ik bake ready
        for i in range(count - 1):
            cmds.addAttr(ik_ctrl[0], ln='fk' + str(i + 1), at='message', h=True)
            cmds.addAttr(fk_ctrl[i], ln='fk', at='message', h=True)
            cmds.connectAttr(ik_ctrl[0] + '.fk' + str(i + 1), fk_ctrl[i] + '.fk')
        cmds.addAttr(ik_ctrl[0], ln='ik1', at='message', h=True)
        cmds.addAttr(ik_ctrl[1], ln='ik', at='message', h=True)
        cmds.connectAttr(ik_ctrl[0] + '.ik1', ik_ctrl[1] + '.ik')

        # organize
        cmds.hide(ik[0], ik2[0])
        cmds.parent(ik[0], ik1_jnt_grp)

        ##twist joint
        if numTwist:
            side = ''
            if ctrlInfo[1] != 'None':
                side = ctrlInfo[1] + '_'

            twistJntsUp, firstTwistJnt = rigUtils.twist(name="{}{}UpTwist".format(side, node), control=ik_ctrl[0],
                                                        parent=self.rigGrp, \
                                                        count=numTwist, stable=fk_ctrl[0], _twist=fk_ctrl[1],
                                                        wu=(1, 0, 0), wuo=self.rigGrp, \
                                                        scale=ik[0])
            cmds.orientConstraint(firstTwistJnt, jnt[0], mo=True)
            twistJntsLo = rigUtils.twist(name="{}{}LoTwist".format(side, node), control=ik_ctrl[0], parent=fk_ctrl[-3], \
                                         count=numTwist, stable=fk_ctrl[-3], _twist=fk_ctrl[-2], \
                                         scale=ik[1])[0]
            for twistJnt in twistJntsUp + twistJntsLo:
                sknTwistJntName = twistJnt.replace('_jnt', '_sknJnt')
                if side:
                    sknTwistJntName = sknTwistJntName.replace(side, '')
                sknTwistJnt = rigUtils.joint(position=twistJnt, orientation=twistJnt, name=preName + sknTwistJntName,
                                             parent=twistJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                             radius=0.35)
                cmds.connectAttr(assemblyAsset + '.joints', sknTwistJnt + '.v')
                sknJnt.append(sknTwistJnt)

        # selectable joints
        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        cmds.select(self.rigGrp)
        cmds.refresh()

        return sknJnt
