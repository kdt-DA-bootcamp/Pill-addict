from sqlalchemy.dialects.mysql import LONGTEXT
from app.database import Base
import sqlalchemy as sa



class BodyFunction(Base):
    __tablename__ = "body_function"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    body = sa.Column(sa.String(100), nullable=False)
    function = sa.Column(sa.String(500), nullable=False)



class Ingredient(Base):
    __tablename__ = "ingredient"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    prms_dt = sa.Column(sa.String(8))
    raw_material = sa.Column(sa.String(255), index=True)  # APLC_RAWMTRL_NM
    function_text = sa.Column(sa.Text)  # FNCLTY_CN
    caution = sa.Column(sa.Text)  # IFTKN_ATNT_MATR_CN
    bssh_nm = sa.Column(sa.String(255))  # BSSH_NM
    recognition_no = sa.Column(sa.String(32))  # HF_FNCLTY_MTRAL_RCOGN_NO
    day_intake = sa.Column(sa.String(255))  # DAY_INTK_CN
    industry = sa.Column(sa.String(255))  # INDUTY_NM
    address = sa.Column(sa.String(255))  # ADDR



class Supplement(Base):
    __tablename__ = "supplement"
    PRDLST_REPORT_NO = sa.Column(sa.BigInteger, primary_key=True)
    PRDLST_NM = sa.Column(sa.String(255)) 
    PRIMARY_FNCLTY = sa.Column(sa.Text)
    RAWMTRL_NM = sa.Column(sa.Text)
    IFTKN_ATNT_MATR_CN = sa.Column(sa.Text)
    FRMLC_MTHD = sa.Column(sa.String(255))
    PRDT_SHAP_CD_NM = sa.Column(sa.String(255))
    LAST_UPDT_DTM = sa.Column(sa.String(10)) 
    PRMS_DT = sa.Column(sa.String(10)) 
    LCNS_NO = sa.Column(sa.String(50)) 
    BSSH_NM = sa.Column(sa.String(255)) 
    CHILD_CRTFC_YN = sa.Column(sa.String(10))
    ETC_RAWMTRL_NM = sa.Column(sa.Text) 
    FRMLC_MTRQLT = sa.Column(sa.String(255)) 
    CSTDY_MTHD = sa.Column(sa.String(255)) 
    NTK_MTHD = sa.Column(sa.Text) 
    HIENG_LNTRT_DVS_NM = sa.Column(sa.String(255))
    PRODUCTION = sa.Column(sa.String(255))
    CAP_RAWMTRL_NM = sa.Column(sa.Text)
    STDR_STND = sa.Column(sa.Text)
    PRDLST_CDNM = sa.Column(sa.String(255)) 
    INDUTY_CD_NM = sa.Column(sa.String(255))
    DISPOS = sa.Column(sa.String(255))  
    POG_DAYCNT = sa.Column(sa.String(255)) 
    INDIV_RAWMTRL_NM = sa.Column(sa.Text) 



class AllergyCategory(Base):
    __tablename__ = "allergy_category"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    category = sa.Column(sa.String(255))
    raw_material = sa.Column(sa.Text)



class FunctionIngredient(Base):
    __tablename__ = "function_ingredient"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    function = sa.Column(sa.String(100), nullable=False)
    ingredient = sa.Column(LONGTEXT, nullable=False)
