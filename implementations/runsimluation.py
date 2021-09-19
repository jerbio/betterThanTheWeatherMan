import numpy
import random
import math
import ast
import json


import sys
import os
import time


PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from datafiles.simultationDistribution import indexDistribution
from libfiles.weatherutility import getSymbolTickerDataForDayIndex, getDayIndexes, timeFromDayIndex, dayIndexFromTime, getRemotePredictions
from libfiles.loaddataseries import load_time_series_daily
from libfiles.idealpricedsymbols import allTheSymbols, turnTheKey, nasdaqPennys, subSetOfTech, healthcare, SubsetOfFinance

foundSymbols = ['AAOI','AAON','AAPL','AAXJ','ABB','ABCB','ABMD','ABTX','ACAD','ACIA','ACLS','ACMR','ACWI','ACWX','ADBE','ADI','ADP','ADRE','ADSK','ADUS','ADVM','AEB','AEIS','AEL','AERI','AFG','AFGH','AFL','AGCO','AGIO','AGN','AGND','AGO','AGZD','AHPI','AIA','AIG','AIMT','AIZ','AJG','AKAM','AKCA','ALAC','ALACU','ALG','ALGN','ALGT','ALKS','ALL','ALLE','ALLK','ALLT','ALLY','ALNY','ALR','ALRM','ALSN','ALV','ALXN','AMAT','AMBA','AMCI','AMCIU','AMD','AME','AMED','AMGN','AMHC','AMKR','AMP','AMPH','AMSF','AMTD','AMWD','ANAB','ANAT','ANGO','ANIP','ANSS','AON','AOS','AOSL','APB','APLS','APLT','APPF','APPN','APRE','ARAV','ARCE','ARCT','ARGX','ARNA','ARTNA','ARVN','ARWR','ARYA','ARYAU','ASB','ASFI','ASML','ASND','ASTE','ATEX','ATLC','ATNI','ATRC','ATVI','AUBN','AVAV','AVGO','AWI','AXAS','AXNX','AXS','AXSM','AYI','AZPN','AZZ','B','BAC','BANC','BAND','BANF','BAP','BBC','BBH','BBP','BBSI','BCBP','BCH','BCML','BCOV','BCPC','BDC','BDTX','BEAT','BFC','BFYT','BGNE','BGRN','BHLB','BIB','BIDU','BIIB','BIOC','BK','BKU','BL','BLD','BLKB','BLPH','BLUE','BMA','BMI','BMO','BMRN','BND','BNDW','BNDX','BNFT','BNS','BNTC','BNTX','BOH','BOKF','BPMC','BPOP','BRC','BRKR','BRKS','BRO','BRP','BRPAU','BSAC','BSTC','BSVN','BTEC','BWA','BWB','BWFG','BXS','BYND','BYSI','CACC','CALM','CAM','CARA','CASH','CASS','CASY','CAT','CATC','CATH','CB','CBG','CBM','CBMB','CBNK','CBOE','CBPO','CBPX','CBRL','CBSH','CBTX','CBU','CCB','CCMP','CCOI','CCXI','CDEV','CDK','CDL','CDLX','CDNA','CDNS','CDW','CERN','CETX','CFA','CFBI','CFFAU','CFG','CFO','CFR','CFX','CG','CGEN','CGNX','CHCO','CHDN','CHEK','CHKP','CHNGU','CHRS','CHRW','CIB','CIGI','CINF','CIR','CIT','CLA','CLBK','CM','CMA','CMCSA','CME','CMI','CMPR','CNA','CNBKA','CNCE','CNFR','CNMD','CNO','CNST','CNXN','CODX','COF','COHR','COKE','COLB','COLL','COLM','COMM','CONE','CORT','COST','COUP','CPF','CPRT','CPS','CPSI','CR','CRAI','CREE','CRMT','CRSP','CRTX','CRUS','CRVL','CRWD','CS','CSA','CSCO','CSF','CSGS','CSII','CSIQ','CSL','CSOD','CSTR','CSWI','CSX','CTAS','CTSH','CTW','CTXS','CUBI','CUTR','CVCO','CVGW','CVLT','CWST','CXSE','CYBR','CYD','CYTK','DAN','DB','DCPH','DDOG','DE','DEL','DFS','DFVL','DGICB','DGII','DGRW','DHIL','DIOD','DISCB','DJCO','DLPH','DLTR','DMTK','DNKN','DNLI','DOCU','DOOR','DORM','DOX','DRC','DRNA','DSGX','DSPG','DTUL','DTYL','DTZ','DVY','DWAS','DXCM','DXJS','DXLG','EA','EBAY','EDE','EDIT','EEFT','EEMA','EGRX','EHTH','EIDX','EIG','EMB','EMCB','EMR','EMXC','ENPH','ENS','ENSG','ENTA','ENTG','ENZL','EPAY','EPZM','EQBK','ERIE','ESG','ESGD','ESGR','ESGU','ESLT','ESNT','ESPO','ESPR','ESQ','ETFC','ETN','ETSY','EVBG','EVER','EVR','EXAS','EXC','EXEL','EXLS','EXPD','EXPE','EXPO','EYE','EYES','FAB','FAD','FAF','FANG','FARO','FAST','FATE','FB','FBHS','FBNC','FBR','FCAL','FCAP','FCFS','FDBC','FDIV','FDT','FELE','FEX','FEYE','FFBW','FFG','FFIV','FGEN','FGM','FHB','FHY','FIBK','FISI','FISV','FIVE','FIVN','FIXD','FIZZ','FJP','FLAT','FLGT','FLIR','FLOW','FLS','FMB','FMCI','FMCIU','FMHI','FNF','FNWB','FNX','FNY','FOCS','FOLD','FONR','FORM','FORR','FORTY','FOXF','FPXI','FRC','FRPH','FRPT','FSB','FSBW','FSFG','FSLR','FSS','FSV','FSZ','FTA','FTACU','FTC','FTCS','FTDR','FTNT','FTSL','FTSM','FTXL','FWRD','FYC','FYX','GBT','GBX','GDS','GEB','GEH','GENY','GFF','GFNCP','GGG','GH','GHL','GHM','GHSI','GILD','GLIBA','GLPG','GLRE','GLUU','GNMA','GNMK','GNRC','GNTY','GNUS','GO','GOOG','GPAQ','GPAQU','GRC','GRID','GRIF','GRMN','GRPN','GRVY','GS','GSBC','GSHD','GSJ','GTHX','GWB','GWGH','GWPH','HAS','HCCH','HCCHU','HCI','HCM','HCSG','HDB','HELE','HGH','HHT','HI','HIFS','HIG','HLG','HLI','HLNE','HMN','HMST','HNI','HOLX','HOMB','HON','HONE','HQY','HRTG','HSBC','HSC','HSIC','HSII','HSKA','HSTM','HTBI','HTH','HUBB','HUBG','HURN','HVBC','HWKN','HY','HYLS','HYXE','HZNP','IAC','IART','IBB','IBKC','IBKR','IBN','IBTX','IBUY','ICBK','ICCH','ICE','ICFI','ICHR','ICLR','ICPT','ICUI','IDCC','IDEX','IDXX','IEF','IEI','IEP','IEUS','IEX','IGF','IGIB','IGIC','IGMS','IGOV','IGSB','IHC','IJT','ILMN','IMKTA','INCY','INDB','INFO','INGN','INOV','INPX','INTC','INTL','INTU','IONS','IOSP','IOTS','IOVA','IPAR','IPGP','IR','IRBT','IRMD','IROQ','IRTC','ISP','ISRG','ISTB','ISTR','ITEQ','ITIC','ITRI','ITT','ITW','IUSB','IUSG','IUSV','IZEA','JACK','JAGX','JAZZ','JBHT','JBSS','JBT','JCI','JCOM','JD','JJSF','JKHY','JKI','JKS','JOBS','JOUT','JPM','JRJC','JRVR','JSMD','JSML','KAI','KALU','KALV','KB','KBE','KBLM','KBWB','KBWP','KEY','KFRC','KIDS','KLAC','KMPR','KMT','KNL','KNSL','KOD','KPTI','KRE','KRTX','KRYS','KWEB','L','LACQ','LACQU','LAKE','LAMR','LANC','LAZ','LBC','LBRDA','LBRDK','LDEM','LEA','LECO','LEVL','LFAC','LFACU','LFUS','LGIH','LGND','LHCG','LII','LITE','LIVN','LK','LKFN','LKOR','LMAT','LMBS','LMNX','LNC','LNN','LNT','LNTH','LOAC','LOACU','LOB','LOGI','LOGM','LOPE','LPLA','LPSN','LRCX','LRGE','LSTR','LULU','LVGO','LX','LXFR','MANH','MANT','MAR','MARK','MAS','MASI','MBB','MBIN','MBWM','MC','MCHI','MCHP','MCY','MDB','MDGL','MDLZ','MEDP','MET','MFC','MGA','MGEE','MGIC','MGLN','MGPI','MGRC','MHNC','MIDD','MIME','MIST','MKL','MKSI','MLAB','MLI','MLNX','MLR','MMC','MMM','MMSI','MNRO','MNST','MNTA','MOMO','MORN','MPWR','MRCY','MRLN','MRNA','MRTX','MRUS','MRVL','MS','MSBI','MSEX','MSFT','MSP','MSTR','MSVB','MTB','MTCH','MTLS','MTOR','MTSI','MTW','MU','MVIS','MXIM','MYFW','MYGN','MYOK','NAKD','NATH','NATI','NBHC','NBIX','NBRV','NCBS','NDAQ','NDSN','NEBU','NEBUU','NEOG','NICE','NLTX','NMIH','NOAH','NODK','NOVT','NPO','NRBO','NRC','NSIT','NSTG','NTAP','NTCT','NTLA','NTNX','NTRA','NTRS','NUVA','NVCR','NVDA','NVEC','NVEE','NVMI','NWBI','NWL','NWLI','NX','NXPI','NXST','NXTC','NXTG','NYCB','NYMT','OAS','OBAS','OBNK','OCGN','ODFL','ODT','OFED','OFG','OFIX','OFLX','OGI','OKTA','OLED','OLLI','OMCL','OMER','OPBK','OPES','OPESU','OPGNW','OPK','OPY','ORI','OSIS','OSK','OTEX','OTTR','OXFD','PACQ','PAHC','PAYX','PB','PCAR','PCB','PCRX','PCSB','PCTY','PDCO','PDD','PDFS','PDLB','PDP','PEGA','PEP','PETQ','PETS','PFBC','PFBI','PFF','PFG','PFPT','PFS','PGJ','PGR','PGTI','PH','PHAT','PHO','PIH','PJT','PKW','PLAB','PLMR','PLOW','PLPC','PLUS','PLW','PLXS','PNC','PNFP','PNQI','PNR','PNRG','PODD','POOL','POWI','PPH','PPS','PRA','PRAA','PRAH','PRFT','PRFZ','PRGS','PRI','PRLB','PRNB','PRSC','PSCC','PSCD','PSCF','PSCH','PSCI','PSCT','PSET','PSL','PSMT','PTC','PTCT','PTF','PTH','PUK','PVBC','PYPL','PYZ','PZZA','Q','QADA','QCOM','QDEL','QFIN','QGEN','QLYS','QQEW','QQQ','QQXT','QRVO','QTEC','QURE','RARE','RBB','RBC','RBCAA','RCII','RCKT','RDFN','RDN','RDUS','RE','REG','REGN','RETA','RF','RFAP','RFDI','RFEU','RFT','RGA','RGEN','RGLD','RGNX','RJF','RLI','RLMD','RMBS','RNDB','RNDM','RNEM','RNR','ROBO','ROCK','ROK','ROKU','ROLL','ROST','RP','RPD','RRBI','RTH','RUSHA','RVNC','RXN','RY','RYAAY','RYTM','RZA','SAFM','SAFT','SAGE','SAIA','SAL','SAMG','SANM','SBAC','SBNY','SBUX','SCHW','SCON','SCS','SCWX','SCZ','SDG','SDGR','SEDG','SEIC','SENEA','SENEB','SF','SFBS','SFN','SGEN','SHEN','SHIP','SHV','SHY','SIGI','SILK','SIMO','SIVB','SKOR','SKYY','SLAB','SLF','SLGN','SLMBP','SLNO','SLP','SLQD','SLW','SMH','SMRT','SMTC','SNDX','SNPS','SNV','SNY','SOLO','SOXX','SPLK','SPNS','SPSC','SPXC','SPY','SQBG','SRCL','SRDX','SRI','SRNE','SRPT','SRRA','SSB','SSD','SSNC','SSTI','SSYS','STAA','STC','STFC','STJ','STL','STMP','STRA','STT','STX','STXB','SUPN','SUSL','SWAV','SWKS','SXI','SXTC','SYKE','SYNA','SYNH','TAPR','TARA','TBIO','TBK','TBLT','TBNK','TCAP','TCBI','TCMD','TCX','TD','TDAC','TDACU','TDIV','TEAM','TECD','TECH','TELL','TER','TEX','TG','THG','THGA','THR','THRM','TKR','TLND','TLT','TMDI','TMH','TMUS','TNC','TNDM','TNXP','TOTA','TOTAU','TPTX','TQQQ','TREE','TRHC','TRN','TRNX','TROW','TRV','TSC','TSCO','TSEM','TTC','TTD','TTEC','TTEK','TTMI','TTNP','TTOO','TTWO','TVIX','TW','TWOU','TXG','TXN','TXRH','TZAC','TZACU','UBS','UCTT','UEIC','UFPI','UFPT','UGLD','UHAL','ULTA','UMBF','UNM','UPLD','URGN','USB','USIG','USLM','USLV','UTHR','UTMD','UVE','VALU','VBIV','VBND','VBTX','VC','VCIT','VCLT','VCSH','VCTR','VCYT','VECO','VEON','VFH','VGIT','VGLT','VGSH','VGT','VHT','VICR','VIE','VIGI','VIIX','VIRT','VISL','VIVO','VMBS','VMI','VNDA','VNET','VNQI','VONE','VONG','VONV','VOO','VOYA','VRNS','VRNT','VRSK','VRSN','VRTS','VRTU','VRTX','VSAT','VTC','VTHR','VTIP','VTWG','VTWO','VTWV','VWOB','VXUS','VYGR','VYMI','WAB','WABC','WAL','WATT','WB','WBA','WBC','WBK','WBS','WDAY','WDC','WDFC','WEBK','WERN','WF','WFC','WHG','WINA','WING','WINS','WIRE','WIX','WLTW','WMGI','WMS','WNC','WOOD','WRB','WRLD','WSO','WTFC','WTM','WTS','WWD','WYNN','XBI','XBIT','XEL','XELA','XENE','XENT','XLF','XLK','XLNX','XLRN','XLV','XNCR','XOG','XOMA','XRAY','XSPA','XT','XYL','Y','YIN','YMAB','YNDX','YORW','YY','Z','ZBRA','ZEAL','ZG','ZGNX','ZLAB','ZM','ZS']

class WeathermanTimelineSimulator:
    def __init__(self, percentageDelta, purse = 100, symbolData = None, useEarlyExit = True):
        self.purse = purse
        
        self.symbolData = None
        self.percentageDelta = percentageDelta/100
        self.dayIndexToListIndex = {}
        self.orderedDayIndexes = []
        self.simulationTape = None #self.convertDictionaryStringToDict(dictionaryString)
        self.dayDistribution = None #self.initializeIndexDistribution(dayIndexDistribution)
        self.dayIndexToExecutedTrades = {}
        self.percentLossSum = 0
        self.percentGainSum = 0
        self.averagePercentLoss = 0
        self.averagePercentGain = 0
        self.useEarlyExit = useEarlyExit #and False
        self.gainCounter = 0
        self.lossCounter = 0
        self.successRatio = 0
        self.nonLoadedDayIndexes = set()
        self.firstProccessedDayIndex = 0
        self.lastProccessedDayIndex = 0
        self.stopLossIsActive = True
        if symbolData is None:
            stocks = list()
            # stocks.extend(subSetOfTech['symbols'])
            #stocks.extend(SubsetOfFinance['symbols'])
            stocks.extend(foundSymbols)
            #stocks.extend(nasdaqPennys['symbols'])
            # stocks.append("TOPS")
            # stocks.append("CSPI")
            self.loadAllSymbolTickerDataIntoMemory(stocks)
        else:
            self.symbolData = symbolData


    def loadAllSymbolTickerDataIntoMemory(self, tickerSymbols):
        retValue = {}
        for symbol in tickerSymbols:
            tickerData = load_time_series_daily(symbol)
            retValue[symbol] = tickerData
        self.symbolData = retValue

    def loadUsingPredictionList(self, predictions):
        dayIndexToSymbol = {}
        simlationTape = {}
        latestPredictions = []
        
        for prediction in predictions:
            tickerData = prediction['tickerData']
            symbol = tickerData['symbol']
            dayIndex = tickerData['dayIndex']
            
            dayIndexData = None
            symbolPrediction = None
            if dayIndex  in dayIndexToSymbol:
                dayIndexData = dayIndexToSymbol[dayIndex]
            else:
                dayIndexData = {}
                dayIndexToSymbol[dayIndex] = dayIndexData
            
            if symbol in dayIndexData and tickerData['timeOfPrediction'] < dayIndexData[symbol]['timeOfPrediction']:
                symbolPrediction = dayIndexData[symbol]
            else:
                symbolPrediction = tickerData
                tickerData['predictionDayIndex'] = dayIndex
                dayIndexData[symbol] = symbolPrediction

        
        for dayIndexPredictions in dayIndexToSymbol.values():
            symbolPredictions = dayIndexPredictions.values()
            latestPredictions.extend(symbolPredictions)

        distribution = self.predictionsToEvaluation(latestPredictions)


        for dayIndex in dayIndexToSymbol:
            toBeBoughtStocks = list(dayIndexToSymbol[dayIndex].values())
            dayDistribution = [{
                
            }]
            simlationTape[dayIndex] = dayDistribution
            dayDistribution[0]['toBeBoughtStocks'] = toBeBoughtStocks
                

        dayIndexes = simlationTape.keys()
        self.updateDayIndexMapping(dayIndexes)

        self.simulationTape = simlationTape
        self.dayDistribution = self.initializeIndexDistribution(distribution)
        
    
    def loadUsingTextDump(self, dictionaryString, dayIndexDistribution):
        self.simulationTape = self.convertDictionaryStringToDict(dictionaryString)
        self.dayDistribution = self.initializeIndexDistribution(dayIndexDistribution)


    def predictionsToEvaluation(self, predictions):
        symbolMapped = self.symbolData
        allSymbols = set()
        dayIndexToSymbolMap = {}
        
        for prediction in predictions:
            if 'dayIndex' in prediction and 'symbol' in prediction:
                dayIndex = prediction['dayIndex']
                symbol = prediction['symbol']
                allSymbols.add(symbol)
                symbolMap = {}
                if dayIndex not in dayIndexToSymbolMap:
                    dayIndexToSymbolMap[dayIndex] = symbolMap
                else:
                    symbolMap = dayIndexToSymbolMap[dayIndex]

                predictionList = []
                if symbol in symbolMap:
                    predictionList = symbolMap[symbol]
                else:
                    symbolMap[symbol] = predictionList

                
                
                predictionList.append(prediction)



        jaraDayCountForItToRain = 7
        dayCountForItToRain = jaraDayCountForItToRain
        
        distributionIndex = [0]*jaraDayCountForItToRain
        pctThreshold = 3
        thresholdMultiplier = (1+(pctThreshold/100))
        allPct = []
        for dayIndex in dayIndexToSymbolMap.keys():
            symbolsMapping = dayIndexToSymbolMap[dayIndex]
            symbols = symbolsMapping.keys()
            for symbol in symbols:
                tickerData = None
                if symbol in symbolMapped and 'symbolData' in symbolMapped[symbol] and dayIndex in symbolMapped[symbol]['symbolData']:
                    tickerData = symbolMapped[symbol]['symbolData'][dayIndex]
                
                if tickerData is not None:
                    closingPrice = tickerData['ticker'][3]
                    formatedIndexes = symbolMapped[symbol]['formatedIndexes']
                    dayIndexToListIndex = formatedIndexes['dayIndexToListIndex']
                    orderedDayIndex = formatedIndexes['orderedDayIndex']
                    nextIndex = dayIndexToListIndex[dayIndex]+1
                    dayIndexListIndexes = []
                    prediction = dayIndexToSymbolMap[dayIndex][symbol]
                    if(nextIndex < len(orderedDayIndex)):
                        dayIndexListIndexes = orderedDayIndex[nextIndex: nextIndex+dayCountForItToRain]
                        if len(dayIndexListIndexes) > 0:
                            dayIndexesForSymbols = dayIndexListIndexes # [orderedDayIndex[indexOfDayIndex] for indexOfDayIndex in dayIndexListIndexes]
                            dayIndexTickerData = [symbolMapped[symbol]['symbolData'][tickerDayIndex] for tickerDayIndex in  dayIndexesForSymbols]
                            highTickerPrices = [tickerPrice['ticker'][2]  for tickerPrice in dayIndexTickerData]
                            thresholdPrice = closingPrice*thresholdMultiplier
                            for index in range(len(highTickerPrices)):
                                stockHighPrice = highTickerPrices[index]
                                if stockHighPrice >= thresholdPrice:
                                    distributionIndex[index] += 1
                            
                            

                            highestPrice = max(highTickerPrices)
                            bestPct = ((highestPrice - closingPrice)/closingPrice) * 100
                            result = 0
                            if bestPct >= pctThreshold:
                                result = 1
                            
                            prediction[0]['result'] = result
                            prediction[0]['prediction'] = 1
                            allPct.append(bestPct)


        return distributionIndex

        # if len(allPct) > 0:
        #     pctResults = [pct for pct in allPct if pct >= pctThreshold]
        #     percentSuccess = (len(pctResults)/len(allPct)) * 100 
        #     # print('You would have cashed in '+str(percentSuccess) + "pct of the time")
        #     retValue = [percentSuccess, len(allPct)]
        #     return retValue
        # else: return None

    def initializeIndexDistribution(self, indexDistribution):
        begin = 0
        end = int(len(indexDistribution))

        retValue = {
            'indexBounds': {'begin': begin, 'end': end},
            'distribution': list(indexDistribution),
        }
        retValue['dayCount'] = len(retValue['distribution'])
        retValue['randomSequence'] = random.choices(range(begin, end), weights=retValue['distribution'], k = 1000)
        return retValue

    def convertDictionaryStringToDict(self, dictionaryString):
        retValue = ast.literal_eval(dictionaryString)

        dayIndexes = retValue.keys()
        self.updateDayIndexMapping(dayIndexes)
        self.nonLoadedDayIndexes = set()
        return retValue
        

    def updateDayIndexMapping(self, dayIndexes):
        orderedDayIndexes = list(dayIndexes)
        orderedDayIndexes.sort()
        index = 0
        self.dayIndexToListIndex = {}
        for dayIndex in orderedDayIndexes:
            self.dayIndexToListIndex[dayIndex] = index
            index+= 1

        self.orderedDayIndexes = orderedDayIndexes

    def getDayIndexDelta(self):
        retValue = random.choice(self.dayDistribution['randomSequence']) + 1
        return retValue
    
    def incrementDayIndex(self, currentDayIndex, delta, symbol):
        isLoadedIndex = False
        # indexOfDays = self.dayIndexToListIndex[currentDayIndex]
        dayIndexes = getDayIndexes(self.symbolData, symbol,currentDayIndex,delta+1 )
        updatedIndex = dayIndexes[len(dayIndexes) - 1]
        if updatedIndex in self.dayIndexToListIndex:
            isLoadedIndex = True
            retValue = updatedIndex
            if retValue in self.nonLoadedDayIndexes:# if dayIndex isn't loaded from storage or read file
                isLoadedIndex = False
        else:
            isLoadedIndex = False
            retValue = currentDayIndex + delta
        return {
            'dayIndex': retValue,
            'isLoadedIndex': isLoadedIndex,
            }

    # def getExecutionPrice(self, dayIndex, symbol):
    #     return 0.9999

    def getEarliestDayDeltaIndexAbovePercentageDelta(self, symbol, currentDayIndex):
        maxDayDelta = self.dayDistribution['dayCount']
        currentDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)
        closingPrice = currentDayTicker[3]
        gainPrice = closingPrice * (1+self.percentageDelta)
        formatedIndexes = self.symbolData[symbol]['formatedIndexes']
        dayIndexToListIndex = formatedIndexes['dayIndexToListIndex']
        beginningIndex = dayIndexToListIndex[currentDayIndex]+1
        
        orderedDayIndex = formatedIndexes['orderedDayIndex']
        possibleDayIndexes = orderedDayIndex[beginningIndex:beginningIndex+maxDayDelta]
        dayDeltaCounter = 1
        foundOne = False
        for dayIndex in possibleDayIndexes:
            futureDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, dayIndex)
            futureDayHighPrice = futureDayTicker[2]
            if futureDayHighPrice >= gainPrice:
                foundOne = True
                break
            dayDeltaCounter+=1
        
        if not foundOne:
            raise NameError('You are broken no time in future hits threshold')
        return dayDeltaCounter



    def checkStopLoss(self, symbol, currentDayIndex, dayDelta):
        retValue = {
            'isActivated': False,
            'multiplier': None,
            'updatedDayIndexData': None,
        }
        if self.stopLossIsActive:
            transitionDayIndexes = getDayIndexes(self.symbolData, symbol, currentDayIndex, dayDelta+1)
            transitionDayIndexes.pop(0)
            currentTickerData = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)
            purchasePrice = currentTickerData[3]
            percentTrigger = self.percentageDelta * 2 #+ 0.1 #- 0.01
            thresholdPrice = purchasePrice * (1 - (percentTrigger))
            stopLossActivated = -1
            dayCounter = 1 # plus because of transitionDayIndexes.pop(0) 
            for transitionDayIndex in transitionDayIndexes:
                tickerPrices = getSymbolTickerDataForDayIndex(self.symbolData, symbol, transitionDayIndex)
                for tickerPrice in tickerPrices[:4]:
                    if tickerPrice < thresholdPrice:
                        stopLossActivated = transitionDayIndex
                        break
                
                if stopLossActivated != -1:
                    break
                dayCounter += 1

            isStopActivated = stopLossActivated != -1
            
            
            if isStopActivated:
                (multiplier, updatedDayIndexData) = self.executeLoss(currentDayIndex, symbol, dayCounter, -percentTrigger)
                retValue['isActivated'] = isStopActivated
                retValue['multiplier'] = multiplier
                retValue['updatedDayIndexData'] = updatedDayIndexData

        return retValue


    def executeLoss (self, currentDayIndex, symbol, dayDelta = None, forcePercentDelta = None):
        multiplier = None
        updatedDayIndexData = None
        if self.symbolData is not None and forcePercentDelta is None:
            # multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.2, 1))) )))
            if dayDelta is None:
                dayDelta = self.dayDistribution['dayCount']
            incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta, symbol)
            updatedDayIndexData = incrementResult['dayIndex']
            if not incrementResult['isLoadedIndex']:
                multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.2, 1))) )))
                self.addIndexToOrderedDayIndexes(updatedDayIndexData)
                return (multiplier, updatedDayIndexData)

            currentDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)
            nextDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, updatedDayIndexData)
            percentDelta = (nextDayTicker[3] - currentDayTicker[3])/currentDayTicker[3]
            if percentDelta > .01:
                 percentDelta = 0.0
            multiplier = 1 + percentDelta
            
        else:
            if forcePercentDelta is None:
                multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.2, 1))) )))
            else:
                multiplier = (1 + forcePercentDelta)
            if dayDelta is None:
                dayDelta = self.dayDistribution['dayCount']
            incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta, symbol)
            updatedDayIndexData = incrementResult['dayIndex']
            if not incrementResult['isLoadedIndex']:
                self.addIndexToOrderedDayIndexes(updatedDayIndexData)
                return (multiplier, updatedDayIndexData)

        return (multiplier, updatedDayIndexData)



    def executeTrade(self, stock, availableRatio):
        symbol = stock['symbol']

        multiplier = None
        currentDayIndex = stock['predictionDayIndex']

        isWinTrade = stock['result'] == 1

        overHalfIndex = self.dayDistribution['dayCount'] /2
        overHalfIndex = math.ceil(overHalfIndex)-1


        # try:
        if isWinTrade:
            multiplier = (1 + self.percentageDelta)
            #dayDelta = self.getDayIndexDelta()
            dayDelta = self.getEarliestDayDeltaIndexAbovePercentageDelta(symbol, currentDayIndex)


            earliestDayExit = overHalfIndex if self.useEarlyExit else dayDelta
            stopLossResult = self.checkStopLoss(symbol, currentDayIndex, earliestDayExit)
            isStopLossActivated = stopLossResult['isActivated']

            if not isStopLossActivated:
                if (self.useEarlyExit and dayDelta > overHalfIndex):
                    (multiplier, updatedDayIndexData) = self.executeLoss(currentDayIndex, symbol, overHalfIndex)
                else:
                    incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta, symbol)
                    updatedDayIndexData = incrementResult['dayIndex']
                    if not incrementResult['isLoadedIndex']:
                        self.addIndexToOrderedDayIndexes(updatedDayIndexData)
            else:
                multiplier = stopLossResult['multiplier']
                updatedDayIndexData  = stopLossResult['updatedDayIndexData']
        else:
            earliestDayExit = overHalfIndex if self.useEarlyExit else self.dayDistribution['dayCount']
            stopLossResult = self.checkStopLoss(symbol, currentDayIndex, earliestDayExit)
            isStopLossActivated = stopLossResult['isActivated']

            if not isStopLossActivated:
                if (self.useEarlyExit):
                    (multiplier, updatedDayIndexData) = self.executeLoss(currentDayIndex, symbol, overHalfIndex)
                    # stopLossResult = self.checkStopLoss(symbol, currentDayIndex, earliestDayExit)
                else:
                    lossResult = self.executeLoss(currentDayIndex, symbol)
                    multiplier = lossResult[0]
                    updatedDayIndexData  = lossResult[1]
            else:
                multiplier = stopLossResult['multiplier']
                updatedDayIndexData  = stopLossResult['updatedDayIndexData']
                
        
        if availableRatio > 0:
            if multiplier < 1:
                self.lossCounter += 1
                self.percentLossSum += (1 - multiplier)
            else:
                self.percentGainSum += (multiplier - 1)
                self.gainCounter += 1
        updatedPrice = multiplier * availableRatio
        self.updateFuturePrice(updatedDayIndexData, updatedPrice)

    def updateFuturePrice(self, updatedDayIndexData, updatedPrice):
        priceUpdates = []
        if updatedDayIndexData in self.dayIndexToExecutedTrades:
            priceUpdateConfig = self.dayIndexToExecutedTrades[updatedDayIndexData]
            priceUpdates = priceUpdateConfig['priceUpdates']
            priceUpdateConfig['isRealized'] = False
        else:
            self.dayIndexToExecutedTrades[updatedDayIndexData] = {
                'priceUpdates': priceUpdates,
                'isRealized': False
            }

        priceUpdates.append(updatedPrice)



    def addIndexToOrderedDayIndexes(self, dayIndex):
        indexes = list(self.orderedDayIndexes)
        indexes.append(dayIndex)
        indexes = list(set(indexes))
        indexes.sort()
        self.nonLoadedDayIndexes.add(dayIndex)
        self.updateDayIndexMapping( indexes)



    def realizeTrades(self, dayIndex):
        retValue = False
        if dayIndex in self.dayIndexToExecutedTrades:
            retValue = True
            priceUpdateConfig = self.dayIndexToExecutedTrades[dayIndex]
            priceUpdates = priceUpdateConfig['priceUpdates']
            priceUpdateConfig['isRealized'] = True
            for priceUpdate in priceUpdates: 
                self.purse += priceUpdate

        return retValue


    def letsDance(self):
        dayIndexKeys = list(self.simulationTape.keys())
        dayIndexKeys.sort()
        dayIndexCounter = len(dayIndexKeys)
        dayRandomLimit = 12
        indexCounter = random.choices(range(dayRandomLimit))[0]
        # indexCounter = 0
        # indexCounter = int(dayIndexCounter/2)
        processedDaIndexes = set()
        divisor = 2
        countLimit = int((len(self.orderedDayIndexes))/divisor)
        self.firstProccessedDayIndex = self.orderedDayIndexes[indexCounter]
        while indexCounter < countLimit:
            dayIndex = self.orderedDayIndexes[indexCounter]
            processedDaIndexes.add(dayIndex)
            self.realizeTrades(dayIndex)
            if(dayIndex in self.simulationTape):
                boughtStocks = self.simulationTape[dayIndex][0]['toBeBoughtStocks']
                if boughtStocks is not None and len(boughtStocks) > 0:
                    numberOfStocks = len(boughtStocks)
                    prevPurse = self.purse
                    pursePerStock = float(((self.purse))/numberOfStocks)
                    for stock in boughtStocks:
                        stockData = stock
                        if 'symbol' not in stock:
                            stockData = stock['lowestPrediction']
                        self.executeTrade(stockData, pursePerStock)
                        self.purse -= pursePerStock
                        if self.purse < 0:
                            self.purse = 0

            indexCounter += 1
            countLimit = int((len(self.orderedDayIndexes))/divisor)


        countLimit = int((len(self.orderedDayIndexes)))
        self.lastProccessedDayIndex = self.orderedDayIndexes[indexCounter - 1]
        while indexCounter < countLimit:
            dayIndex = self.orderedDayIndexes[indexCounter]
            processedDaIndexes.add(dayIndex)
            tradeIsRealized = self.realizeTrades(dayIndex)
            if tradeIsRealized:
                self.lastProccessedDayIndex = dayIndex
            indexCounter += 1

        
        isAllRealized = True
        for tradeDayIndex in self.dayIndexToExecutedTrades:
            isAllRealized = self.dayIndexToExecutedTrades[tradeDayIndex]['isRealized']
            if not isAllRealized:
                print("MAY DAY! MAY DAY!! \n You didn't collect all your profits")
                break
        

        self.successRatio = (self.gainCounter/(self.gainCounter + self.lossCounter)) * 100
        print("all trades were realized " + str(isAllRealized))
        print("success ratio " + str(self.successRatio))

        self.averagePercentLoss = self.percentLossSum/self.lossCounter
        self.averagePercentGain = self.percentGainSum/self.gainCounter


def runMSimulationsFromRemotePredictions(simulationCount = 500):
    global foundSymbols
    excludedSymbols = set()
    excludedSymbols.add('IOTS')
    indexCounter = 0
    sumOfSimulations = 0

    sumOfAveragesPercentLosses =  0
    sumOfAveragesPercentGains =  0

    def groupAnalysis(predictions):
        pctToPredictions = {}
        retValue = []
        for prediction in predictions:
            if 'tickerData' in prediction and prediction['tickerData'] is not None:
                loadedJson = json.loads(prediction['tickerData'])
                prediction['tickerData'] = loadedJson
                retValue.append(prediction)
                if 'extrapolatedTicker' in loadedJson:
                    extrapolatedTicker = loadedJson['extrapolatedTicker']
                    closePrice = extrapolatedTicker[3]
                    openPrice = extrapolatedTicker[0]
                    pct = ((closePrice - openPrice)/openPrice) * 100
                    pctAppr = round(pct , 0)
                    predictionsForPct = []
                    if pctAppr in pctToPredictions:
                        predictionsForPct = pctToPredictions[pctAppr]
                    else:
                        pctToPredictions[pctAppr] = predictionsForPct

                    predictionsForPct.append(prediction)
            
        return retValue


    minMultiplier = None
    maxMultiplier = None
    
    predictions = getRemotePredictions()
    predictions = [prediction for prediction in predictions if prediction['symbol'] not in excludedSymbols]
    dedupedSymbols = [prediction['symbol'] for prediction in predictions]
    foundSymbols = list(set(dedupedSymbols))

    categoryGrouping = {}

    for prediction in predictions:
        if 'weatherManPredictionConfig' in prediction:
            config = prediction['weatherManPredictionConfig']
            if 'category' in config:
                category = config['category']
                categoryList = None
                if category in categoryGrouping:
                    categoryList = categoryGrouping[category]
                else:
                    categoryList = []
                    categoryGrouping[category] = categoryList

                categoryList.append(prediction)

    percentDelta = 3

    simulationInitObj = WeathermanTimelineSimulator(percentDelta, 1)
    # print(str(categoryGrouping.keys()))
    stockCategory = 'tech'
    predictions = categoryGrouping[stockCategory]

    parsedPredictions = groupAnalysis(predictions)

    simulationInitObj.loadUsingPredictionList(parsedPredictions)
    
    stopLossFlag = False
    earlyExitFlag = False


    numberOfDaysInYear = 365
    sumOfNumberOfYEars = 0
    while indexCounter < simulationCount:
        moneySimulation = WeathermanTimelineSimulator(percentDelta, 1, symbolData = simulationInitObj.symbolData, useEarlyExit=True)
        moneySimulation.loadUsingPredictionList(parsedPredictions)
        moneySimulation.stopLossIsActive = stopLossFlag
        moneySimulation.useEarlyExit = earlyExitFlag
        moneySimulation.letsDance()
        beginDayIndex = moneySimulation.firstProccessedDayIndex
        endDayIndex = moneySimulation.lastProccessedDayIndex
        dayDiff = endDayIndex - beginDayIndex

        numberOfYears = dayDiff/numberOfDaysInYear
        sumOfSimulations += moneySimulation.purse
        sumOfAveragesPercentLosses += moneySimulation.averagePercentLoss
        sumOfAveragesPercentGains += moneySimulation.averagePercentGain
        indexCounter+=1

        sumOfNumberOfYEars += numberOfYears

        if minMultiplier is None or moneySimulation.purse < minMultiplier:
            minMultiplier = moneySimulation.purse

        if maxMultiplier is None or moneySimulation.purse > maxMultiplier:
            maxMultiplier = moneySimulation.purse

    averageMultiplier = sumOfSimulations/indexCounter
    averageAveragesPercentLosses = sumOfAveragesPercentLosses/indexCounter
    averageAveragesPercentGains = sumOfAveragesPercentGains/indexCounter
    averageNumberOfYears = sumOfNumberOfYEars/indexCounter
    print('stop Loss is '+str("Active" if stopLossFlag else "Inactive"  ) )
    print('early exit is '+str("Active" if earlyExitFlag else "Inactive"  ) )
    print('average multiplier is '+str(averageMultiplier) )
    print('range of multiplier is '+str(minMultiplier)+' - ' +str(maxMultiplier))
    print('average percentage Loss is '+str(averageAveragesPercentLosses) )
    print('average percentage Gain is '+str(averageAveragesPercentGains) )
    print('Average number of years '+str(averageNumberOfYears))
    print('Stock category is '+str(stockCategory))



runMSimulationsFromRemotePredictions(200)


def runMultipleSimulations(simulationCount = 500):
    filePath = '.\\datafiles\\simultationtape.txt'
    file = open(filePath, "r")
    contents = file.read()
    indexCounter = 0

    sumOfSimulations = 0

    sumOfAveragesPercentLosses =  0
    sumOfAveragesPercentGains =  0

    minMultiplier = None
    maxMultiplier = None

    percentDelta = 3
    simulationInitObj = WeathermanTimelineSimulator(percentDelta, 1)
    simulationInitObj.loadUsingTextDump(contents, indexDistribution)
    
    stopLossFlag = False
    earlyExitFlag = False


    numberOfDaysInYear = 365
    sumOfNumberOfYEars = 0
    while indexCounter < simulationCount:
        moneySimulation = WeathermanTimelineSimulator(percentDelta, 1, symbolData = simulationInitObj.symbolData, useEarlyExit=True)
        moneySimulation.loadUsingTextDump(contents, indexDistribution)
        moneySimulation.stopLossIsActive = stopLossFlag
        moneySimulation.useEarlyExit = earlyExitFlag
        moneySimulation.letsDance()
        beginDayIndex = moneySimulation.firstProccessedDayIndex
        endDayIndex = moneySimulation.lastProccessedDayIndex
        dayDiff = endDayIndex - beginDayIndex

        numberOfYears = dayDiff/numberOfDaysInYear
        sumOfSimulations += moneySimulation.purse
        sumOfAveragesPercentLosses += moneySimulation.averagePercentLoss
        sumOfAveragesPercentGains += moneySimulation.averagePercentGain
        indexCounter+=1

        sumOfNumberOfYEars += numberOfYears

        if minMultiplier is None or moneySimulation.purse < minMultiplier:
            minMultiplier = moneySimulation.purse

        if maxMultiplier is None or moneySimulation.purse > maxMultiplier:
            maxMultiplier = moneySimulation.purse

    averageMultiplier = sumOfSimulations/indexCounter
    averageAveragesPercentLosses = sumOfAveragesPercentLosses/indexCounter
    averageAveragesPercentGains = sumOfAveragesPercentGains/indexCounter
    averageNumberOfYears = sumOfNumberOfYEars/indexCounter
    print('stop Loss is '+str("Active" if stopLossFlag else "Inactive"  ) )
    print('early exit is '+str("Active" if earlyExitFlag else "Inactive"  ) )
    print('average multiplier is '+str(averageMultiplier) )
    print('range of multiplier is '+str(minMultiplier)+' - ' +str(maxMultiplier))
    print('average percentage Loss is '+str(averageAveragesPercentLosses) )
    print('average percentage Gain is '+str(averageAveragesPercentGains) )
    print('Average number of years '+str(averageNumberOfYears))


# runMultipleSimulations(200)