import pyZiagn

Test5 = pyZiagn.uniaxialTensileTest(
    length0=75, Area0=20.73
)  # if uCrosshead lenght0=33
Test5.Title = 'Test5'
Test5.TestMachine = 'unibz MTS E0.10 upper'
Test5.dataSets = ['uCrosshead', 'Force', 't', 'uExtensometer']
Test5.importTestData('data/5D.txt')
Test5.disp = -Test5.uExtensometer
Test5.disp = Test5.uCrosshead
Test5.changeUnits()
Test5.plotForceDisp()
# Test5.cutData("disp", 3.7)
# Test5.smoothForce()
Test5.plotForceDisp()
Test5.calcStressEng()
Test5.calcStrainEng()
Test5.plotStressStrainEng()
Test5.calcStressTrue()
Test5.calcStrainTrue()
Test5.plotStressStrainTrue()
Test5.plotStressStrainEngTrue()
Test5.calcElasticModulus(strain0=0.0000, strain1=0.001)
Test5.zeroStrain()
Test5.calcRP02()
Test5.calcLinearLimit()
Test5.calcStressUltimate()
Test5.calcLength()
Test5.calcArea()
Test5.calcBreak()
Test5.plotStressStrainEngAll()
print(Test5.stressUltimate)
print(Test5.stressEng[-1])
print(Test5.stressRP02)
print(Test5.stressLinLimit)
print(Test5.YoungsModulus)
