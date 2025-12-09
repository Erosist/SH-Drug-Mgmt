import sqlite3
import sys
p = r'E:/ShareCache/lyx/Thild/软件工程/小组/项目/SH-Drug-Mgmt/backend/instance/data.db'
try:
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS __writetest (id INTEGER PRIMARY KEY, t TEXT)')
    cur.execute("INSERT INTO __writetest (t) VALUES ('test_from_check')")
    conn.commit()
    print('sqlite write OK')
except Exception as e:
    print('sqlite write FAILED:', e)
    sys.exit(1)
finally:
    try:
        conn.close()
    except:
        pass
