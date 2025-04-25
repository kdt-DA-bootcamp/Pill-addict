
from sqlalchemy.dialects.mysql import LONGTEXT
from app.database import Base
import sqlalchemy as sa

class BodyFunction(Base):
    __tablename__ = "body_function"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    body = sa.Column(sa.String(100), nullable=False)
    function = sa.Column(sa.String(255), nullable=False)


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

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    report_no = sa.Column(sa.String(32), unique=True, index=True)  # PRDLST_REPORT_NO
    product_name = sa.Column(sa.String(255))  # PRDLST_NM
    primary_function = sa.Column(sa.Text)  # PRIMARY_FNCLTY
    raw_materials = sa.Column(sa.Text)  # RAWMTRL_NM
    caution = sa.Column(sa.Text)  # IFTKN_ATNT_MATR_CN
    formulation = sa.Column(sa.String(255))  # FRMLC_MTHD
    product_shape = sa.Column(sa.String(255))  # PRDT_SHAP_CD_NM
    last_updated = sa.Column(sa.String(10))  # LAST_UPDT_DTM
    approval_date = sa.Column(sa.String(10))  # PRMS_DT
    license_no = sa.Column(sa.String(50))  # LCNS_NO
    bssh_nm = sa.Column(sa.String(255))  # BSSH_NM
    child_certified = sa.Column(sa.String(10))  # CHILD_CRTFC_YN
    etc_raw = sa.Column(sa.Text)  # ETC_RAWMTRL_NM
    quality = sa.Column(sa.String(255))  # FRMLC_MTRQLT
    storage = sa.Column(sa.String(255))  # CSTDY_MTHD
    intake_method = sa.Column(sa.Text)  # NTK_MTHD
    high_func_type = sa.Column(sa.String(255))  # HIENG_LNTRT_DVS_NM
    production = sa.Column(sa.String(255))  # PRODUCTION
    cap_raw = sa.Column(sa.Text)  # CAP_RAWMTRL_NM
    standard = sa.Column(sa.Text)  # STDR_STND
    category_name = sa.Column(sa.String(255))  # PRDLST_CDNM
    industry_code = sa.Column(sa.String(255))  # INDUTY_CD_NM
    disposal = sa.Column(sa.String(255))  # DISPOS
    expiry = sa.Column(sa.String(255))  # POG_DAYCNT
    indiv_raw = sa.Column(sa.Text)  # INDIV_RAWMTRL_NM

class AllergyCategory(Base):
    __tablename__ = "allergy_category"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    category = sa.Column(sa.String(255))  # 알러지 카테고리
    raw_material = sa.Column(sa.Text)  # 원재료




class FunctionIngredient(Base):
    __tablename__ = "function_ingredient"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    function = sa.Column(sa.String(100), nullable=False)
    ingredient = sa.Column(LONGTEXT, nullable=False)
