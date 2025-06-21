import os

def main():
    print('paste image filenames:')
    fns = []
    while True:
        op = input('> ').strip()
        if not op:
            break
        fns.append(op)
    # fns = [*reversed(fns)]
    print()
    print(fns)
    input('Press Enter to continue...')
    for fn in fns:
        stem, ext = os.path.splitext(fn)
        cmd = f'ffmpeg -i {fn} {stem}_f.jpg'
        print(f'{cmd = }')
        os.system(cmd)
    print('ok')

if __name__ == '__main__':
    main()
