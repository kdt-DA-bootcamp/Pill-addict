# run_pipeline.py
import json
import pandas as pd
import config            # 경로·모델·API 키 등
import pipeline          # 우리가 방금 고친 pipeline.py

# ---------------------------------------------------------------------------
# Helper ─ 영양제 DB 로더
# ---------------------------------------------------------------------------
def load_supplement_data(json_path: str) -> list[dict]:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"▶️ 영양제 데이터 로드 완료: {len(data)}개 ({json_path})")
        return data
    except FileNotFoundError:
        print(f"[Error] 영양제 DB 파일이 없습니다: {json_path}")
    except json.JSONDecodeError:
        print(f"[Error] JSON 파싱 오류: {json_path}")
    except Exception as e:
        print(f"[Error] 영양제 DB 로드 중 예외: {e}")
    return []

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("🚀 파이프라인 테스트 시작")

    # ---------------- 사용자·파일 설정 ----------------
    user_name        = "이루시아"
    user_gender      = "여성"
    health_exam_file = "/Users/lucia/Desktop/영양제/database/이루시아검진결과.pdf"

    file_type = "pdf" if health_exam_file.lower().endswith(".pdf") else "image"
    print(f"\n[사용자] {user_name} / {user_gender}")
    print(f"[파일]   {health_exam_file} ({file_type})")

    # ---------------- 파일 로드 ----------------
    try:
        with open(health_exam_file, "rb") as f:
            file_bytes = f.read()
    except Exception as e:
        print(f"[Error] 건강검진 파일 읽기 실패: {e}")
        return

    # ---------------- 파이프라인 ----------------
    print("\n--- 1) OCR & 파싱 ---")
    exam_dict, _ = pipeline.parse_health_exam(file_bytes, file_type)
    print("▶️ 추출 결과:", exam_dict)

    ref_data = pipeline.load_reference()
    abnormal = pipeline.find_abnormal(exam_dict, ref_data, user_gender)
    print("▶️ 이상치:", abnormal)

    ingredients = pipeline.get_ingredients_from_abnormal_tuple(abnormal)
    print("▶️ 추천 성분:", ingredients)

    # ---------------- 제품 추천 ----------------
    supp_db_path = getattr(config, "SUPPLEMENT_DATA_PATH", None)
    supp_data    = load_supplement_data(supp_db_path) if supp_db_path else []
    products     = pipeline.recommend_products(ingredients, supp_data, top_n=3)

    if products:
        print("▶️ 추천 제품:")
        for p in products:
            print(f"  - {p.get('PRDLST_NM','제품명 없음')} / {p.get('BSSH_NM','제조사 없음')}")
    else:
        print("▶️ 추천할 제품 없음")

    # ---------------- 성분·MSD 정보 로드 ----------------
    ing_info_df = (
        pipeline.load_ingredient_info()
        if hasattr(config, "INGREDIENT_JSON_PATH")
        else pd.DataFrame()
    )
    msd_manual = (
        pipeline.load_msd_manual()
        if hasattr(config, "MSD_MANUAL_JSON_PATH")
        else {}
    )

    # ---------------- GPT 호출 ----------------
    print("\n--- 2) GPT 응답 생성 ---")
    final = pipeline.build_structured_data(
        exam=exam_dict,
        abnormal=abnormal,
        ingredients=ingredients,
        products=products,
        ing_info_df=ing_info_df,
        msd_info=msd_manual,
        user_name=user_name,
    )
    print("\n📝 GPT 응답:\n", final.get("gpt_response", "응답 없음"))

    print("\n✅ 테스트 완료")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
