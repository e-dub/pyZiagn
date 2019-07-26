import numpy as np
import matplotlib.pyplot as plt
from matplotlib2tikz import save as tikz_save
import pandas as pd


class uniaxialTensileTest(object):
    def __init__(self, TestMachine="unibz MTS E0.10", Title="",
                 length0=10, Area0=10):
        self.Area0 = Area0
        self.TestMachine = []
        self.Title = Title
        self.Area0 = Area0
        self.length0 = length0

    def loadExample(self):
        self.Area0 = 10
        self.length0 = 10
        self.nSamples = 10001
        self.Force = np.linspace(0, 1000, self.nSamples)
        self.disp = np.linspace(0, 1, self.nSamples)
        self.ForceUnit = "N"
        self.dispUnit = "mm"
        self.Titel = "Simple test case"

    def changeUnits(self, UnitSystem="MPa"):
        if UnitSystem == "MPa":
            if self.dispUnit == "m":
                self.disp *= 1000
                self.dispUnit = "mm"
            if self.ForceUnit == "kN":
                self.Force *= 1000
                self.dispUnit = "mm"

    def calcStressEng(self):
        self.stressEng = self.Force/self.Area0

    def calcStressTrue(self):
        self.stressTrue = self.stressEng*(1+self.strainEng)

    def calcStrainEng(self):
        self.strainEng = self.disp/self.length0

    def calcStrainTrue(self):
        self.strainTrue = np.log(1+self.strainEng)

    def calcElasticModulus(self, strain0=0, strain1=0.1):
        self.ElasticModulus = np.zeros((self.nSamples-1,))
        for i in range(self.nSamples-1):
            self.ElasticModulus[i] = ((self.stressEng[i+1]-self.stressEng[i]) /
                                      (self.strainEng[i+1]-self.strainEng[i]))
        stressEngElastic = self.stressEng[self.strainEng > strain0]
        strainEngElastic = self.strainEng[self.strainEng > strain0]
        stressEngElastic = stressEngElastic[strainEngElastic < strain1]
        strainEngElastic = strainEngElastic[strainEngElastic < strain1]
        self.ElasticTrend = np.poly1d(np.polyfit(strainEngElastic,
                                                 stressEngElastic, 1))
        self.YoungsModulus = ((self.ElasticTrend(strain1) -
                               self.ElasticTrend(strain0))/(strain1 - strain0))

    def calcStressUltimate(self):
        self.stressUltimate = max(self.stressEng)
        self.strainUltimate = self.strainEng[np.where(self.stressEng ==
                                                      self.stressUltimate)]

    def calcArea(self):
        self.Area = self.Area0/(1 + self.strainEng)

    def calcRp02(self):
        self.stressRP02 = self.stressEng[np.argwhere(np.diff(np.sign(self.ElasticTrend(self.strainEng-0.002) - self.stressEng)) != 0)][0][0]
        self.strainRP02 = self.strainEng[np.argwhere(np.diff(np.sign(self.ElasticTrend(self.strainEng-0.002) - self.stressEng)) != 0)][0][0]

    def calcLinearLimit(self, eps=0.025, strainRangeMax=0.02):
        self.stressLinLimit = self.stressEng[abs((self.ElasticTrend(self.strainEng) - self.stressEng)/self.stressEng < eps)][-1]
        self.strainLinLimit = self.strainEng[abs((self.ElasticTrend(self.strainEng) - self.stressEng)/self.stressEng < eps)][-1]
        if self.stressLinLimit > self.stressRP02:
            strainRangeCut = self.strainEng[self.strainEng < strainRangeMax]
            stressRangeCut = self.stressEng[self.strainEng < strainRangeMax]
            self.stressLinLimit = stressRangeCut[abs((self.ElasticTrend(strainRangeCut[strainRangeCut < 0.04]) - stressRangeCut)/stressRangeCut < eps)][-1]
            self.strainLinLimit = strainRangeCut[abs((self.ElasticTrend(strainRangeCut[strainRangeCut < 0.04]) - stressRangeCut)/stressRangeCut < eps)][-1]

    def smoothForce(self):
        from scipy.signal import savgol_filter
        self.ForceRaw = self.Force.copy()
        self.Force = savgol_filter(self.ForceRaw, 101, 3)

    def cutData(self, parameter, value):
        if parameter == "disp":
            self.dispAll = self.disp.copy()
            self.ForceAll = self.Force.copy()
            self.nSamplesAll = self.nSamples
            self.disp = self.disp[self.dispAll < value]
            self.Force = self.Force[self.dispAll < value]
            self.nSamples = len(self.disp)

    def importTestData(self, FileName, FileFormat="MTScsv", ForceUnit="N",
                       dispUnit="mm", decimalSeparator=","):
        self.FileFormat = FileFormat
        self.rawData = pd.read_csv(FileName, sep='\t', header=None,
                                   decimal=decimalSeparator,
                                   skiprows=(0, 1, 2, 3, 4, 5, 6, 7))
        self.disp = self.rawData[0].values
        self.dispUnit = "mm"
        self.Force = self.rawData[1].values
        self.ForceUnit = "kN"
        self.nSamples = len(self.disp)

    def zeroStrain(self):
        stress0 = self.stressEng[0]
        self.strain0 = stress0/self.YoungsModulus
        self.strainEng += self.strain0

    def plotForceDisp(self, Show=True, SaveTex=True, SavePng=True,
                      SaveSvg=True):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 5))
        plt.grid(True)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(self.disp, self.Force)
        plt.ylabel('Force $F$ [N]')
        plt.xlabel('Displacement $u$ [mm]')
        plt.title(self.Title)
        plt.xlim(xmin=0)
        plt.ylim(ymin=0)
        plt.tight_layout()
        if SaveTex:
            tikz_save(self.Title+'_ForceDisp.tex', show_info=False,
                      strict=False, figureheight='\\figureheight',
                      figurewidth='\\figurewidth',
                      extra_axis_parameters={"axis lines*=left"})
        if SavePng:
            plt.savefig(self.Title+"_ForceDisp.png", format="png")
        if SaveSvg:
            plt.savefig(self.Title+"_ForceDisp.svg", format="svg")
        if Show:
            plt.show()

    def plotStressStrainEng(self, Show=True, SaveTex=True, SavePng=True,
                            SaveSvg=True):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 5))
        plt.grid(True)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(self.strainEng, self.stressEng)
        plt.ylabel('Engineering stress $\\sigma_{\\mathrm{Eng}}$ [MPa]')
        plt.xlabel('Engineering strain $\\varepsilon_{\\mathrm{Eng}}$ [-]')
        plt.title(self.Title)
        plt.xlim(xmin=0)
        plt.ylim(ymin=0)
        plt.tight_layout()
        if SaveTex:
            tikz_save(self.Title+'_StressStrainEng.tex', show_info=False,
                      strict=False, figureheight='\\figureheight',
                      figurewidth='\\figurewidth',
                      extra_axis_parameters={"axis lines*=left"})
        if SavePng:
            plt.savefig(self.Title+"_StressStrainEng.png", format="png")
        if SaveSvg:
            plt.savefig(self.Title+"_StressStrainEng.svg", format="svg")
        if Show:
            plt.show()

    def plotStressStrainTrue(self, Show=True, SaveTex=True, SavePng=True,
                             SaveSvg=True):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 5))
        plt.grid(True)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(self.strainTrue, self.stressTrue)
        plt.ylabel('True stress $\\sigma_{\\mathrm{True}}$ [MPa]')
        plt.xlabel('True strain $\\varepsilon_{\\mathrm{True}}$ [-]')
        plt.title(self.Title)
        plt.xlim(xmin=0)
        plt.ylim(ymin=0)
        plt.tight_layout()
        if SaveTex:
            tikz_save(self.Title+'_StressStrainTrue.tex', show_info=False,
                      strict=False, figureheight='\\figureheight',
                      figurewidth='\\figurewidth',
                      extra_axis_parameters={"axis lines*=left"})
        if SavePng:
            plt.savefig(self.Title+"_StressStrainTrue.png", format="png")
        if SaveSvg:
            plt.savefig(self.Title+"_StressStrainTrue.svg", format="svg")
        if Show:
            plt.show()

    def plotStressStrainEngTrue(self, Show=True, SaveTex=True, SavePng=True,
                                SaveSvg=True):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 5))
        plt.grid(True)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(self.strainEng, self.stressEng,
                 label='Engineering stress–strain')
        plt.plot(self.strainTrue, self.stressTrue,
                 label='True stress–strain')
        plt.ylabel('Stress $\\sigma$ [MPa]')
        plt.xlabel('Strain $\\varepsilon$ [-]')
        plt.legend(frameon=False)
        plt.title(self.Title)
        plt.xlim(xmin=0)
        plt.ylim(ymin=0)
        plt.tight_layout()
        if SaveTex:
            tikz_save(self.Title+'_StressStrainEngTrue.tex', show_info=False,
                      strict=False, figureheight='\\figureheight',
                      figurewidth='\\figurewidth',
                      extra_axis_parameters={"axis lines*=left"})
        if SavePng:
            plt.savefig(self.Title+"_StressStrainEngTrue.png", format="png")
        if SaveSvg:
            plt.savefig(self.Title+"_StressStrainEngTrue.svg", format="svg")
        if Show:
            plt.show()

    def plotForceDispSmoothRaw(self, Show=True, SaveTex=True, SavePng=True,
                               SaveSvg=True):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 5))
        plt.grid(True)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(self.dispAll, self.ForceAll,
                 label='Raw data')
        plt.plot(self.disp, self.Force,
                 label='Smoothed and cut')
        plt.ylabel('Force $F$ [N]')
        plt.xlabel('Displacement $u$ [mm]')
        plt.legend(frameon=False)
        plt.title(self.Title)
        plt.xlim(xmin=0)
        plt.ylim(ymin=0)
        plt.tight_layout()
        if SaveTex:
            tikz_save(self.Title+'_ForceDispSmoothRaw.tex', show_info=False,
                      strict=False, figureheight='\\figureheight',
                      figurewidth='\\figurewidth',
                      extra_axis_parameters={"axis lines*=left"})
        if SavePng:
            plt.savefig(self.Title+"_ForceDispSmoothRaw.png", format="png")
        if SaveSvg:
            plt.savefig(self.Title+"_ForceDispSmoothRaw.svg", format="svg")
        if Show:
            plt.show()

    def plotStressStrainEng02(self, yMax=50, xMax=0.075, Show=True,
                              SaveTex=True, SavePng=True, SaveSvg=True):
        strain1 = np.linspace(0.0, max(self.strainEng), self.nSamples)
        strain2 = np.linspace(0.002, max(self.strainEng), self.nSamples)
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 5))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.plot(self.strainEng, self.stressEng, label="Material behavior")
        #plt.plot(self.strainEng+0.002+self.strain0, self.ElasticTrend(self.strainEng), label="0.2% offset")
        plt.plot(strain1, self.ElasticTrend(strain1-self.strain0), '--',
                 label="Young's modulus")
        plt.plot(strain2, self.ElasticTrend(strain2-0.002-self.strain0), '--',
                 label="0.2% offset")
        plt.plot(self.strainEng[0], self.stressEng[0], ".",
                 label="Initial state of test")
        plt.plot(self.strainRP02+self.strain0, self.stressRP02, "o",
                 label="$R_{P0.2}$")
        plt.plot(self.strainLinLimit+self.strain0, self.stressLinLimit, "o",
                 label="Linear limit")
        plt.plot(self.strainUltimate+self.strain0, self.stressUltimate, "o",
                 label="Ultimate strength")
        plt.plot(self.strainEng[-1], self.stressEng[-1], "x", label="Break")
        plt.ylabel('Engineering stress $\\sigma_{\\mathrm{Eng}}$ [MPa]')
        plt.xlabel('Engineering strain $\\varepsilon_{\\mathrm{Eng}}$ [-]')
        plt.title(self.Title)
        plt.xlim(xmin=0, xmax=xMax)
        #plt.ylim(ymin=0, ymax=max(self.stressEng)*1.05)
        plt.ylim(ymin=0, ymax=yMax)
        plt.grid(True)
        plt.legend(frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        if SaveTex:
            tikz_save(self.Title+'_StressStrainEng02.tex', show_info=False,
                      strict=False, figureheight='\\figureheight',
                      figurewidth='\\figurewidth',
                      extra_axis_parameters={"axis lines*=left"})
        if SavePng:
            plt.savefig(self.Title+"_StressStrainEng02.png", format="png")
        if SaveSvg:
            plt.savefig(self.Title+"_StressStrainEng02.svg", format="svg")
        if Show:
            plt.show()


def export2Excel(TestList, FileName="TestSummary.xlsx", PrintData=True):
    TestData = {"Test": [i.Title for i in TestList],
                "Young's modulus": [i.YoungsModulus for i in TestList],
                "Initial stress of test": [i.stressEng[0] for i in TestList],
                "Stress at linear limit": [i.stressLinLimit for i in TestList],
                "Rp0.2": [i.stressRP02 for i in TestList],
                "Ultimate stress": [i.stressUltimate for i in TestList],
                "Breaking stress": [i.stressEng[-1] for i in TestList],
                "Breaking strain": [i.strainEng[-1] for i in TestList]}
    TestDataFrame = pd.DataFrame(TestData, columns=["Test", "Young's modulus",
                                                    "Initial stress of test",
                                                    "Stress at linear limit",
                                                    "Rp0.2", "Ultimate stress",
                                                    "Breaking stress",
                                                    "Breaking strain"])
    TestDataFrame.to_excel(FileName, index=None, header=True)
    if PrintData:
        print(TestDataFrame)


def plotMulti(TestList, Show=True, SaveTex=True, SavePng=True, SaveSvg=True,
              PlotName="Comparison"):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    markers = ["s", "v", "^", "o", "D", "+"]
    for i in range(len(TestList)):
        plt.plot(TestList[i].strainEng, TestList[i].stressEng,
                 marker=markers[int(TestList[i].Title[-1])-1], markevery=500,
                 color='C'+str(int(TestList[i].Title[0])-1),
                 label=TestList[i].Title)
    plt.ylabel('Engineering stress $\\sigma_{\\mathrm{Eng}}$ [MPa]')
    plt.xlabel('Engineering strain $\\varepsilon_{\\mathrm{Eng}}$ [-]')
    plt.xlim(xmin=0, xmax=0.075)
    #plt.ylim(ymin=0, ymax=max(self.stressEng)*1.05)
    plt.ylim(ymin=0, ymax=55)
    plt.legend(frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    if Show:
        plt.show()
    if SaveTex:
        tikz_save(PlotName+'_.tex', show_info=False, strict=False,
                  figureheight='\\figureheight', figurewidth='\\figurewidth',
                  extra_axis_parameters={"axis lines*=left"})
    if SavePng:
        plt.savefig(PlotName+".png", format="png")
    if SaveSvg:
        plt.savefig(PlotName+".svg", format="svg")


if __name__ == "__main__":
    print("Test of package")
    Test1 = uniaxialTensileTest()
    Test1.loadExample()
    Test1.changeUnits()
    Test1.plotForceDisp()
