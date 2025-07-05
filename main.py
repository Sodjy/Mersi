from window import MainWindow
import logging

def main():
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        window = MainWindow()
        window.mainloop()
        
    except Exception as e:
        logging.error("Uncaught exception", exc_info=e)
        raise e

if __name__ == "__main__":
    main()