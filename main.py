from covex_label_manager.gui import start

if __name__=='__main__':
    import sys
    if len(sys.argv)==3 and sys.argv[1]=='--self-check':
        from covex_label_manager.self_check import run
        run(sys.argv[2])
    else:
        start()
