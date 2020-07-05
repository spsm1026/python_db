import pickle
import os
import re
import sqlalchemy as db
from sqlalchemy.sql import text
import cx_Oracle

engine = db.create_engine("oracle://hr:hr@oraxe11g/xe")
conn = engine.connect()

def main():
    cust_list = []
    cust_list, page = load_cust(cust_list)
    while True:
        choice = print_menu()
        if choice == "I":
            cust_list, page, customer, statement = input_cust(cust_list, page)
        elif choice == "C":
            print_c(cust_list, page)
        elif choice == "P":
            page = print_p(cust_list, page)
        elif choice == "N":
            page = print_n(cust_list, page)
        elif choice == "U":
            update_cust(cust_list, statement, customer)
        elif choice == "D":
            page = delete_cust(cust_list, page)
        elif choice == "S":
            save_cust(customer, statement)
        elif choice == "Q":
            break
        else:
            print("메뉴를 잘못입력했읍니다.")


def print_menu():
    return input("""
        다음 중 작업 하실 메뉴를 입력 하세요.
        I - 고객 정보 입력
        C - 현재 고객 정보 출력
        P - 이전 고객 정보 출력
        N - 다음 고객 정보 출력
        U - 고객 정보 수정
        D - 고객 정보 삭제
        S - 데이타 저장
        Q - 프로그램 종료
        """).strip().upper()


def input_cust(cust_list, page):
    print("고객 정보 입력 로직")
    customer = {"name": "", "gender": "", "email": "", "birthyear": ""}
    while True:
        name = input("이름을 입력 하세요 : ")
        regex = re.compile("[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z]")
        if regex.search(name):
            break
        else:
            print("이름은 한글로만 입력하세요.")

    while True:
        gender = input("성별(M/F/O)을 입력 하세요 : ").upper()
        if gender in ("M", "F", "O"):
            break
        else:
            print("성별은 M/F/O 중에서만 입력하세요.")

    while True:
        email = input("이메일 주소를 입력 하세요 : ")
        regex = re.compile(
            "^[a-zA-Z][a-zA-Z0-9]{3,10}@[a-zA-Z]{2,6}[.][a-zA-Z]{2,4}$")
        if regex.search(email):  # True, False 0 == False, -2 == True
            break
        else:
            print("이메일은 example@example.com 형식으로 입력하세요. 아이디는 최소 4자 이상.")

    while True:
        birthyear = input("출생 년도를 입력 하세요 : ")
        regex = re.compile("^[0-9]{4}$")
        if regex.search(birthyear):
            break
        else:
            print("출생년도 4자리를 입력하세요.")

    customer["name"] = name
    customer["gender"] = gender
    customer["email"] = email
    customer["birthyear"] = birthyear
    cust_list.append(customer)

    with engine.begin() as conn:
        statement = text(
            """INSERT INTO cust(name, gender, email, birthyear)
            VALUES
            (:name, :gender, :email, :birthyear)""")
        conn.execute(statement, **customer)
    

    page = len(cust_list)-1
    return cust_list, page, customer, statement


def print_c(cust_list, page):
    print("현재 고객 정보 출력")
    if page >= 0:
        print(cust_list[page])
    else:
        print("입력된 정보가 없습니다.")


def print_p(cust_list, page):
    print("이전 고객 정보 출력")
    if page <= 0 or len(cust_list) == 0:
        print("첫 번째 페이지 입니다.")
    else:
        page = page - 1
        with engine.connect() as conn:
            statement = text(
                """SELECT * FROM cust WHERE ROWNUM = {}""".format(page + 1)
            )
            conn.execute(statement)
        
    return page


def print_n(cust_list, page):
    print("다음 고객 정보 출력")
    if page >= len(cust_list)-1:
        print("마지막 번째 페이지 입니다.")
    else:
        page = page + 1
        with engine.connect() as conn:
            statement = text(
                """SELECT * FROM cust WHERE ROWNUM = {}""".format(page + 1)
            )
            conn.execute(statement)
    return page


def update_cust(cust_list, statement, customer):
    while True:
        choice1 = input("수정하고 싶은 고객 정보의 이름을 입력하세요 : ")
        idx = -1
        for i, val in enumerate(cust_list):
            # if cust_list[i]["name"] == choice1.strip():
            if val["name"] == choice1.strip():
                idx = i
                break
        if idx == -1:
            print("등록되지 않은 이름입니다.")
            break

        choice1 = input("""수정하고싶은 항목을 입력하세요
        name, gender, email, birthyer, cancel
        """)
        if choice1 in ("name", "gender", "email", "birthyear"):
            cust_list[idx][choice1] = input(
                "수정할 {}을 입력 하세요. ".format(choice1))

            with engine.begin() as conn:
                statement = text(
                    """UPDATE SET cust(name, gender, email, birthyear)
                    VALUES
                    (:name, :gender, :email, :birthyear)
                    
                    WHERE {} ={} """.format(choice1,cust_list[idx][choice1]))

                conn.execute(statement, **customer)
                break
        elif choice1 == "cancel":
            break
        else:
            print("존재하지 않는 항목입니다.")
            break
        


def delete_cust(cust_list, page):
    print("고객 정보 삭제")
    statement = text(
        """DELETE FROM cust
        WHERE name ={}""".format(cust_list[page]['name'])
    )
    save_cust(cust_list[page], statement)
    cust_list, page = load_cust(cust_list)
    return page


def save_cust(customer, statement):
    with engine.begin() as conn:
        conn.execute(statement, **customer)


def load_cust(cust_list):
    with engine.connect() as conn:
        cust_list = conn.execute("SELECT * FROM cust")
        return cust_list


if __name__ == "__main__":
    main()
