from sqlite3 import connect, Error as sqlError, Row
import InitData
from datetime import datetime
from simplePred import predict
import streamlit as st


class DBController:
  def __init__(self, db_path):
    self.__db = connect(db_path)
    self.__db.row_factory = Row
    c = self.db.cursor()
    if not c.execute("""SELECT name FROM sqlite_master""").fetchall():
      print("Existing database not found at path")
      self.init_db()
      

  @property
  def db(self):
    return self.__db

  def init_db(self):
    try:
      c = self.db.cursor()
      c.executescript(InitData.init)
      print("Database schema initialised successfully.")

      c.executescript(InitData.policys)
      print("Policy data added successfully.")
      self.db.commit()
      
      c.executescript(InitData.policyHolders)
      print("PolicyHolders data added successfully.")
      self.db.commit()
      
      c.executescript(InitData.brokers)
      print("Broker data added successfully.")
      self.db.commit()
      
      c.executescript(InitData.claims)
      print("Claims data added successfully.")
      self.db.commit()
      
      c.executescript(InitData.aims)
      print("Aims data added successfully.")
      self.db.commit()

    except sqlError as e:
      self.db.rollback()
      open("dbLog.txt", "a").write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - " + str(e) + "\n")
      print(f"ERROR: {e}")


class NotFoundError(Exception):
  def __init__(self, err):
    open("dbLog.txt", "a").write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - " + str(err) + "\n")
    print(f"ERROR: {err}")
    
class Data():
  def __init__(self, dbc):
    self.__dbc = dbc
  
  @property
  def brokerList(self):
    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT Name
                FROM Brokers, Policys
                WHERE strftime('%Y', StartDate) == strftime('%Y', 'now')      
                """).fetchall()
    
    brokerNames = []
    for i in data:
      if i['Name'] not in brokerNames:
        brokerNames.append(i['Name'])
    
    return brokerNames
  
  @property
  def subClassList(self):
    c = self.__dbc.db.cursor()
    data = c.execute(f"""
                SELECT SubClass
                FROM Policys
                WHERE LineOfBusiness in {f"({', '.join(map(repr, st.session_state.LoB))})"}
                AND strftime('%Y', StartDate) == strftime('%Y', 'now') 
                """).fetchall()
    
    classNames = []
    for i in data:
      if i['SubClass'] not in classNames:
        classNames.append(i['SubClass'])
    
    return classNames
  @property
  def lineOfBusinessList(self):
    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT LineOfBusiness
                FROM Policys
                WHERE strftime('%Y', StartDate) == strftime('%Y', 'now')      
                """).fetchall()
    
    lobNames = []
    for i in data:
      if i['LineOfBusiness'] not in lobNames:
        lobNames.append(i['LineOfBusiness'])
    
    return lobNames
  
  @property
  def coverageList(self):
    c = self.__dbc.db.cursor()
    data = c.execute(f"""
                SELECT Coverage
                FROM Policys
                WHERE LineOfBusiness in {f"({', '.join(map(repr, st.session_state.LoB))})"} 
                AND strftime('%Y', StartDate) == strftime('%Y', 'now') 
                """).fetchall()
    
    coverageNames = []
    for i in data:
      if i['Coverage'] not in coverageNames:
        coverageNames.append(i['Coverage'])
    
    return coverageNames
  
  @property
  def jurisdictionList(self):
    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT Jurisdiction
                FROM Policys   
                WHERE strftime('%Y', StartDate) == strftime('%Y', 'now')      
                """).fetchall()
    
    placeNames = []
    for i in data:
      if i['Jurisdiction'] not in placeNames:
        placeNames.append(i['Jurisdiction'])
    return placeNames

  def calcPerc(self, filters):
     c = self.__dbc.db.cursor()
     if filters == {} and st.session_state.selections == {}:
        countBlock = c.execute("""
                    SELECT COUNT(PolicyID) as count
                    FROM Policys
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    """).fetchone()
     else:
        query = """SELECT COUNT(PolicyID) as count
                    FROM Policys, Brokers
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    AND Policys.BrokerID == Brokers.BrokerID
                    """ 
        for i in filters:
            try:
                filters[i] = sum(filters[i], [])
            except:
               pass
            temp = f"({', '.join(map(repr, filters[i]))}"
            query += f"\nAND {i} in {temp})"
        for i in st.session_state.selections:
            temp = f"({', '.join(map(repr, st.session_state.selections[i]))})"
            query += f"\nAND {i} in {temp}"  
        countBlock = c.execute(query).fetchone()
     
     if st.session_state.selections == {}:
        countCurrent = c.execute("""
                    SELECT COUNT(PolicyID) as count
                    FROM Policys
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    """).fetchone()
     else:
        query = """SELECT COUNT(PolicyID) as count
                    FROM Policys, Brokers
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    AND Policys.BrokerID == Brokers.BrokerID
                    """ 
        for i in st.session_state.selections:
            query += f"\nAND {i} in {f"({', '.join(map(repr, st.session_state.selections[i]))})"}"
        countCurrent = c.execute(query).fetchone()
        
     return countBlock['count'] / countCurrent['count']


class Graph():
  def __init__(self, dbc):
    self.__dbc = dbc
    
  def GWP(self, filters):  
    c = self.__dbc.db.cursor()
    if st.session_state.LoB:
        filters['LineOfBusiness'] = st.session_state.LoB
    if filters == {}:
        data = c.execute("""
                    SELECT GrossWP, StartDate
                    FROM Policys
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    """).fetchall()
    else:
        query = """SELECT GrossWP, StartDate
                    FROM Policys, Brokers
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    AND Policys.BrokerID == Brokers.BrokerID
                    """ 
        for i in filters:
            query += f"\nAND {i} in {f"({', '.join(map(repr, filters[i]))})"}"
        data = c.execute(query).fetchall()
      
    
    YearGWP = {}
    for i in data:
      if i['StartDate'][:7] not in YearGWP:
        YearGWP[i['StartDate'][:7]] = i['GrossWP']
      else:
        YearGWP[i['StartDate'][:7]] += i['GrossWP']
      
    acc = dict(sorted(YearGWP.items()))
    
    cul = {}
    total = 0
    for i in acc:
      total += acc[i]
      cul[i] = total
      
    
    GWPAims = {}
    if filters == {}:
      data = c.execute("""
                SELECT Date, GWP
                FROM Aims
                WHERE strftime('%Y', Date) == strftime('%Y', 'now')       
                """).fetchall()
      total = 0
      for i in data:
        total += i['GWP']
        GWPAims[i['Date'][:7]] = total

        
    aim = dict(sorted(GWPAims.items()))
    

    pred = predict(cul)
    if pred != {}:
        pred[list(cul)[-1]] = cul[list(cul)[-1]]
        pred = dict(sorted(pred.items()))
 
    
    return {'acc' : acc, 'cul': cul, 'aim' : aim, 'pred': pred}
  
  @property
  def GWPYear(self):  
    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT GrossWP, StartDate
                FROM Policys
                WHERE strftime('%Y', StartDate) != strftime('%Y', 'now')      
                """).fetchall()
    
    YearGWP = {}
    for i in data:
      if i['StartDate'][:4] not in YearGWP:
        YearGWP[i['StartDate'][:4]] = i['GrossWP']
      else:
        YearGWP[i['StartDate'][:4]] += i['GrossWP']

    acc = dict(sorted(YearGWP.items()))
    
    return acc


  def BusinessType(self, filters):  
    c = self.__dbc.db.cursor()
    if filters == {}:
        data = c.execute("""
                    SELECT StartDate , PrevPolicy, GrossWP
                    FROM Policys
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now')     
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    """).fetchall()
    else:
        query = """SELECT StartDate , PrevPolicy, GrossWP
                    FROM Policys, Brokers
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    AND Policys.BrokerID == Brokers.BrokerID
                    """ 
        for i in filters:
            query += f"\nAND {i} in {f"({', '.join(map(repr, filters[i]))})"}"
        data = c.execute(query).fetchall()
    
    new = {}
    continued = {}
    for i in data:
      if i['StartDate'][:7] not in new:
        new[i['StartDate'][:7]] = 0
        continued[i['StartDate'][:7]] = 0
      if i['PrevPolicy'] == None:
        new[i['StartDate'][:7]] += i['GrossWP']
      else:
        continued[i['StartDate'][:7]] += i['GrossWP']
        
    new = dict(sorted(new.items()))
    continued = dict(sorted(continued.items()))
    
    YearRetention = {}
    contTotal = 0
    totalTotal = 0
    for i in continued:
      contTotal  += continued[i]
      totalTotal += continued[i] + new[i]
      YearRetention[i] = (contTotal / totalTotal) * 100
      
        
    retention = dict(sorted(YearRetention.items()))
    
    data = c.execute("""
                SELECT Date, RetentionRate
                FROM Aims
                WHERE strftime('%Y', Date) == strftime('%Y', 'now')      
                """).fetchall()
    
    RetentionAims = {}
    for i in data:
        RetentionAims[i['Date'][:7]] = i['RetentionRate']
 
    aim = dict(sorted(RetentionAims.items()))
    
    pred = predict(retention)
    if pred != {}:
        pred[list(retention)[-1]] = retention[list(retention)[-1]]
        pred = dict(sorted(pred.items()))
    
    return {'new' : new, 'cont': continued, 'ret': retention, 'aim' : aim, 'pred': pred}
  

  
  def HitRate(self, filters): 
    c = self.__dbc.db.cursor()
    if st.session_state.LoB:
        filters['LineOfBusiness'] = st.session_state.LoB
    if filters == {}:
        data = c.execute("""
                    SELECT SubmissionStatus, StartDate
                    FROM Policys
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    """).fetchall()
    else:
        query ="""
                    SELECT SubmissionStatus, StartDate
                    FROM Policys, Brokers
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    AND  Policys.BrokerID == Brokers.BrokerID
                    """
        for i in filters:
            query += f"\nAND {i} in {f"({', '.join(map(repr, filters[i]))})"}"
            
        data = c.execute(query).fetchall()
        
    YearStatus = {}
    for i in data:
      if i['StartDate'][:7] not in YearStatus:
        YearStatus[i['StartDate'][:7]] = [0,0,0]
      if i['SubmissionStatus'] == "Submitted":
        YearStatus[i['StartDate'][:7]][0] += 1 
      if i['SubmissionStatus'] == "Quoted":
        YearStatus[i['StartDate'][:7]][1] += 1
      if i['SubmissionStatus'] == "Bound":
        YearStatus[i['StartDate'][:7]][2] += 1
      
    QuotedHit = {}
    BoundHit = {}
    SubBound = {}
    for i in YearStatus:
      QuotedHit[i] = ( (YearStatus[i][1]+YearStatus[i][2]) / (YearStatus[i][0]+YearStatus[i][1]+YearStatus[i][2]) ) * 100
      if (YearStatus[i][1]+YearStatus[i][2]) == 0:
        BoundHit[i] = 0
      else:
        BoundHit[i] = ( YearStatus[i][2] / (YearStatus[i][1]+YearStatus[i][2]) ) * 100
      SubBound[i] = ( YearStatus[i][2] / (YearStatus[i][0]+YearStatus[i][1]+YearStatus[i][2]) ) * 100
    
    subQuote = dict(sorted(QuotedHit.items())) 
    quoteBound = dict(sorted(BoundHit.items())) 
    subBound = dict(sorted(SubBound.items())) 
    
    data = c.execute("""
                SELECT Date, HitRate
                FROM Aims
                WHERE strftime('%Y', Date) == strftime('%Y', 'now')      
                """).fetchall()
    
    HitAims = {}
    if filters != {}:
        total = 0
        for i in data:
          total += i['HitRate']
          HitAims[i['Date'][:7]] = total

      
    aim = dict(sorted(HitAims.items()))
    
    qpred = predict(subQuote)
    if qpred != {}:
        qpred[list(subQuote)[-1]] = subQuote[list(subQuote)[-1]]
        qpred = dict(sorted(qpred.items()))
    
    bpred = predict(quoteBound)
    if bpred != {}:
        bpred[list(quoteBound)[-1]] = quoteBound[list(quoteBound)[-1]]
        bpred = dict(sorted(bpred.items()))
    
    spred = predict(subBound)
    if spred != {}:
        spred[list(subBound)[-1]] = subBound[list(subBound)[-1]]
        spred = dict(sorted(spred.items()))
    
    return {'subQuote': subQuote, 'quoteBound': quoteBound, 'subBound': subBound, 'aim': aim, 'qpred': qpred, 'bpred': bpred, 'spred': spred}
  
  @property
  def GWPByBroker(self): 
    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT Name, GrossWP, StartDate
                FROM Policys, Brokers
                WHERE Policys.BrokerID = Brokers.BrokerID     
                AND strftime('%Y', StartDate) == strftime('%Y', 'now')  
                AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                """).fetchall() 
        
    BrokerGWP = {}
    total = 0
    for i in data:   
      total += i['GrossWP']
      if i['Name'] not in BrokerGWP:
        BrokerGWP[i['Name']] = i['GrossWP']
      else:
        BrokerGWP[i['Name']] += i['GrossWP']
        
    for i in BrokerGWP:
        BrokerGWP[i] = BrokerGWP[i] / total * 100

    return {k: v for k, v in sorted(BrokerGWP.items(), key=lambda item: item[1])}
  

  def ELR(self, filters): 
    c = self.__dbc.db.cursor()
    if st.session_state.LoB:
        filters['LineOfBusiness'] = st.session_state.LoB
    if filters == {}:
        data = c.execute("""
                    SELECT StartDate, GrossWP
                    FROM Policys   
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now')
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    """).fetchall()
        percentage = 1
    else:
        query = """SELECT GrossWP, StartDate
                    FROM Policys, Brokers
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    AND Policys.BrokerID == Brokers.BrokerID
                    """ 
        
        countquery ="""SELECT COUNT(GrossWP) as count
                    FROM Policys, Brokers
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    AND Policys.BrokerID == Brokers.BrokerID
                    """ 
                    
        count = c.execute("""SELECT COUNT(GrossWP) as count
                    FROM Policys
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                    AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                """).fetchone()
        

        for i in filters:
            query += f"\nAND {i} in {f"({', '.join(map(repr, filters[i]))})"}"
            countquery += f"\nAND {i} in {f"({', '.join(map(repr, filters[i]))})"}"
        data = c.execute(query).fetchall()
        countdata = c.execute(countquery).fetchone()
        
        percentage = countdata['count'] / count['count']
        
    MonthGWP = {}
    for i in data:
      if i['StartDate'][:7] not in MonthGWP:
        MonthGWP[i['StartDate'][:7]] = 0
      MonthGWP[i['StartDate'][:7]] += i['GrossWP']
      
    MonthGWP = dict(sorted(MonthGWP.items()))

    MonthGWPCul = {}
    total = 0
    for i in MonthGWP:
      total += MonthGWP[i]
      MonthGWPCul[i] = total

    data = c.execute("""
                SELECT Date, ClaimLoss
                FROM Aims   
                WHERE strftime('%Y', Date) == strftime('%Y', 'now')    
                """).fetchall()


    MonthExpLoss = {}
    for i in data:
        MonthExpLoss[i['Date'][:7]] = i['ClaimLoss'] * percentage
        
    MonthExpLoss = dict(sorted(MonthExpLoss.items()))

    MonthLossCul = {}
    total = 0
    for i in MonthExpLoss:
      total += MonthExpLoss[i]
      MonthLossCul[i] = total

    MonthLossRatio = {}
    MonthLossRatioCul = {}
    
    for i in MonthGWP:
      MonthLossRatio[i] = ( MonthExpLoss[i] / MonthGWP[i] ) * 100
      MonthLossRatioCul[i] = ( MonthLossCul[i] / MonthGWPCul[i] ) * 100

    acc = dict(sorted(MonthLossRatio.items())) 
    cul = dict(sorted(MonthLossRatioCul.items())) 
    
    
    data = c.execute("""
                SELECT Date, ELR
                FROM Aims
                WHERE strftime('%Y', Date) == strftime('%Y', 'now')      
                """).fetchall()
    
    ELRAims = {}
    if filters != {}:
        for i in data:
          ELRAims[i['Date'][:7]] = i['ELR']
        
        aim = dict(sorted(ELRAims.items()))
    else:
        aim = {}
    
    pred = predict(cul)
    if pred != {}:
        pred[list(cul)[-1]] = cul[list(cul)[-1]]
        pred = dict(sorted(pred.items()))
    
    return {'acc': acc, 'aim': aim, 'cul': cul, 'pred': pred}
  

  def RateAdequecy(self, filters):
    c = self.__dbc.db.cursor()
    if st.session_state.LoB:
        filters['LineOfBusiness'] = st.session_state.LoB
    if filters == {}:
        data = c.execute("""
                    SELECT StartDate, GrossWP, TechnicalWP
                    FROM Policys
                    WHERE strftime('%Y', StartDate) == strftime('%Y', 'now')  
                    AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                    """).fetchall()
    else:
      query = """SELECT GrossWP, StartDate, TechnicalWP
                  FROM Policys, Brokers
                  WHERE strftime('%Y', StartDate) == strftime('%Y', 'now') 
                  AND strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                  AND Policys.BrokerID == Brokers.BrokerID
                  """ 
      for i in filters:
          query += f"\nAND {i} in {f"({', '.join(map(repr, filters[i]))})"}"
      data = c.execute(query)
    
    MonthGWP = {}
    MonthTWP = {}
    for i in data:
      if i['StartDate'][:7] not in MonthGWP:
        MonthGWP[i['StartDate'][:7]] = 0
        MonthTWP[i['StartDate'][:7]] = 0
        
      MonthGWP[i['StartDate'][:7]] += i['GrossWP']
      MonthTWP[i['StartDate'][:7]] += i['TechnicalWP']
      

    MonthGWPCul = {}
    MonthTWPCul = {}
    totalGWP = 0
    totalTWP = 0
    for i in dict(sorted(MonthGWP.items())):
      totalGWP += MonthGWP[i]
      totalTWP += MonthTWP[i]
      MonthGWPCul[i] = totalGWP
      MonthTWPCul[i] = totalTWP
      

    MonthRate = {}
    MonthRateCul = {}
    for i in MonthGWP:
      MonthRate[i] = (MonthGWP[i] / MonthTWP[i] - 1) * 100
      MonthRateCul[i] = (MonthGWPCul[i] / MonthTWPCul[i] - 1) * 100
      
   

    acc = dict(sorted(MonthRate.items()))
    cul = dict(sorted(MonthRateCul.items()))
    
    
    pred = predict(cul)
    if pred != {}:
        pred[list(cul)[-1]] = cul[list(cul)[-1]]
        pred = dict(sorted(pred.items()))

    rateAdaquecyAims = {}
    data = c.execute("""
                SELECT Date, RateAdequecy
                FROM Aims  
                WHERE strftime('%Y', Date) == strftime('%Y', 'now')    
                """).fetchall()
    
    aim = {}
    for i in data:
      aim[i['Date']] = i['RateAdequecy']
      
    aim = dict(sorted(rateAdaquecyAims.items()))
      
    return {'acc': acc, 'aim': aim, 'cul': cul, 'pred': pred}
  

  @property
  def SubVolumeByBroker(self):
    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT SubmissionStatus, Name, StartDate
                FROM Policys, Brokers
                WHERE Policys.BrokerID = Brokers.BrokerID 
                AND strftime('%Y', StartDate) == strftime('%Y', 'now') 
                AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')     
                """).fetchall()
    
    BrokerVolume = {}
    TotalSubmitted = 0
    for i in data:
      if i['Name'] not in BrokerVolume:
        BrokerVolume[i['Name']] = [0,0]
      TotalSubmitted += 1
      if i['SubmissionStatus'] == "Bound":
        BrokerVolume[i['Name']][1] += 1
      else:
        BrokerVolume[i['Name']][0] += 1
        
    BrokerSubmittedShare = {}
    BrokerBoundShare = {}
    for i in BrokerVolume:
      BrokerSubmittedShare[i] = (BrokerVolume[i][0] / TotalSubmitted) * 100
      BrokerBoundShare[i] = (BrokerVolume[i][1] / TotalSubmitted) * 100

    return {'sub': BrokerSubmittedShare, 'bound': {k: v for k, v in sorted(BrokerBoundShare.items(), key=lambda item: item[1])}}
  
  @property
  def ExposureMap(self):
    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT PolicyLimit, StartDate, Jurisdiction
                FROM Policys    
                WHERE strftime('%Y', StartDate) == strftime('%Y', 'now')  
                AND  strftime('%Y %m %d', StartDate) <= strftime('%Y %m %d', 'now')
                """).fetchall()
    
    exposure = {}
    for i in data:
      if i['Jurisdiction'] not in exposure:
        exposure[i['Jurisdiction']] = 0
      exposure[i['Jurisdiction']] += i['PolicyLimit']
      
    return exposure
  
  @property
  def RARC(self):
    data = Graph(self.__dbc).GWPYear
    
    YearRARC = {}
    for i in data:
      if str(int(i)-1) not in data:
        YearRARC[i] = 0
      else:
        YearRARC[i] = (data[i] - data[str(int(i)-1)]) / data[str(int(i)-1)] * 100
        
    acc = dict(sorted(YearRARC.items()))

    c = self.__dbc.db.cursor()
    data = c.execute("""
                SELECT Date, RARC
                FROM Aims        
                """).fetchall()
    
    aim = {}
    for i in data:
      aim[i['Date'][:4]] = i['RARC']    
      
    pred = predict(acc)
    pred[list(acc)[-1]] = acc[list(acc)[-1]]
    pred = dict(sorted(pred.items()))

    return {'acc': acc, 'aim' : aim, 'pred': pred}
        
dbc = DBController("database.db")