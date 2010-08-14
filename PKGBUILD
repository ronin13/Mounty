# Maintainer: raghu.prabhu13 

pkgname=mounty
pkgver=0.0.2
pkgrel=1
pkgdesc="Mount drives easily"
arch=(any)
license=('GPL')
install=mounty.install
depends=('pyinotify' 'udev')
optdepends=('python-notify') # If you want libnotify notifications
source=("mounty-${pkgver}.tar.bz2")

build() {
   cd $startdir/src/${pkgname}-${pkgver}
   install -D -m764 mounty $pkgdir/etc/rc.d/mounty
   install -D -m764 mounty.py $pkgdir/usr/bin/mounty
   # Needed for hal to ignore removable media
   if pacman -Q | grep hal;then
	   install -D -m644 20-storage-methods.fdi $pkgdir/etc/hal/fdi/policy/20-storage-methods.fdi
   fi
   install -D -m666 mounty.tab $pkgdir/etc/mounty.tab.example
   install -D -m644 README $pkgdir/usr/share/doc/mounty/README
}
