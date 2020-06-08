
a = "var a=function(){if (!confirm('Confirma o download do documento?')) return false;};var b=function(){if(typeof jsfcljs == 'function'){jsfcljs(document.getElementById('detalheDocumento'),{'detalheDocumento:download':'detalheDocumento:download'},'');}return false};return (a()==false) ? false : b();"

print(a.rfind("return"))

print(a[:a.rfind("return")] + a[a.rfind("return")+6:])