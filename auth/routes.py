from flask import  request, jsonify
from infrastructure.database import getDBConn
from .jwt_utils import generateToken, decodeToken, tokenRequired
from auth.utils import password_hash


def authRoutes(app):
    @app.route('/signup', methods =['POST'])
    def signup():
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if not (username and email and password):
            return jsonify({"error":"Missing required fields"}), 400
        conn = getDBConn()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"message":"User already exist"}), 400
        

        hashedpassword = password_hash.hashPassword(password)


        query = """
            INSERT INTO users(username, email, password) VALUES (%s, %s, %s)
            RETURNING user_id;
        """
        cur.execute(query,(username, email, hashedpassword))
        userid = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()


        accesstoken, refreshtoken = generateToken(userid)

        return jsonify({"message":"user created successfully",
                         "user_id":userid,
                         "access_token" : accesstoken,
                         "refresh_token" : refreshtoken
                         }), 201
    
    @app.route('/login', methods = ['POST'])
    def login():
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        query = '''
                SELECT password, user_id FROM users WHERE username = %s;
        '''
        conn = getDBConn()
        cur = conn.cursor()
        cur.execute(query, (username,))
        if not cur.fetchone:
            cur.close()
            conn.close()
            return jsonify({"message" : "user doesn't exist"}), 500
        
        user = cur.fetchone()
        cur.close()
        conn.close()



        check = password_hash.chechPassword(user[0], password)

        

        if not check:
            return jsonify({"message" : "Entered password is incorrect"}), 401
        
        accesstoken, refreshtoken = generateToken(user[1])
        
        return jsonify({"message" : "user logged in successfully",
                        "access_token" : accesstoken
                        }), 200
    
    @app.route("/edit-profile", methods = ['POST'])
    @tokenRequired
    def editProfile():
        userid = request.user
        data = request.json
        allowed_fields = ["username", "first_name", "last_name", "gender", "address"]

        updates = {key: value for key, value in data.items() if key in allowed_fields}

        if not updates:
            return jsonify({
                "message" : "No valid fields to update"
            }), 400
        
        try:
            conn = getDBConn()
            cur = conn.cursor()

            set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])

            query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
            values = list(updates.values()) + [userid]

            cur.execute(query, values)
            conn.commit()

            return jsonify({
                "message" : "Profile updated successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "error" : str(e)
            }), 500
        finally:
            cur.close()
            conn.close()

    @app.route("/delete-account", methods = ['POST'], endpoint= "delete_account")
    @tokenRequired
    def delete():
        userid = request.user

        try:
            query = """
                DELETE FROM users WHERE user_id = %s;
            """
            conn = getDBConn()
            cur = conn.cursor()
            cur.execute(query, (userid,))
            conn.commit()
            return jsonify({"message" : "Account deleted successfully!"}), 200

        except Exception as e:
            return jsonify({"error" : str(e)}), 500
        finally:
            cur.close()
            conn.close()

 