import os
from PyQt5.QtCore import QFileSystemWatcher, QTimer

class FileWatcher:
    def __init__(self, filepath, on_change_callback, last_contents, start=False):
        self.filepath = filepath
        self.on_change_callback = on_change_callback
        self.last_contents = last_contents
        
        self.paused = False
        
        if start and not os.path.exists(filepath):
            print('FileWatcher: file does not exist, could not start')
            self.running = False
            return
            
        
        self.watcher = QFileSystemWatcher()
        if start:
            print('FileWatcher: watching file ' + filepath)
            
            self.start(filepath)
            self.running = True
            
            # self.poll_file()
            
        else: 
            self.running = False
            
            

        
    def pause(self):
        print('FileWatcher: pause')
        self.paused = True
    
    def resume(self):
        print('FileWatcher: resume')
        self.paused = False
    
    @property
    def isRunning(self):
        return self.running
    
    def start(self, path):
        if self.running:
            self.stop()
        
        self.watcher.removePaths(self.watcher.files())
        self.watcher.removePaths(self.watcher.directories())
        self.watcher.addPath(path)
        
        self.filepath = path
        self.watcher.fileChanged.connect(self.on_file_changed)
        self.running = True
        print('FileWatcher: started, path ' + path)
        
    def stop(self):
        if not self.running: 
            return
        self.watcher.fileChanged.disconnect(self.on_file_changed)
        self.running = False
        print('FileWatcher: stopped')
        
        
    def on_file_changed(self, path):
        print('FileWatcher: internal changed0')
        
        if self.paused:
            return
        
        print('FileWatcher: internal changed')
        QTimer.singleShot(200, self.poll_file)

    def poll_file(self):
        print('FileWatcher: poll')
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                contents = f.read()
            print('c',contents != self.last_contents)
            if contents != self.last_contents:
                self.last_contents = contents
                self.on_change_callback(contents)
        except Exception as e:
            print(f"FileWatcher: Error reading watched file: {e}")
