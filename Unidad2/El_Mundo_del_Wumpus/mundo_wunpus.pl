% Mundo de Wumpus - Agente basado en percepciones con interfaz corregida
% Autor: Implementación en SWI-Prolog con matriz visual

:- use_module(library(pce)).
:- use_module(library(random)).

% Hechos dinámicos para el estado del mundo
:- dynamic(wumpus_pos/2).
:- dynamic(oro_pos/2).
:- dynamic(pozo_pos/2).
:- dynamic(agente_pos/2).
:- dynamic(agente_dir/1).
:- dynamic(tiene_flecha/1).
:- dynamic(wumpus_vivo/1).
:- dynamic(casilla_visitada/2).
:- dynamic(casilla_segura/2).
:- dynamic(casilla_peligrosa/2).
:- dynamic(percepcion_actual/1).
:- dynamic(mundo_creado/1).
:- dynamic(oro_recogido/1).
:- dynamic(juego_terminado/1).

% Predicados de la interfaz gráfica
:- dynamic(ventana/1).
:- dynamic(canvas/1).
:- dynamic(casillas/1).

% Inicialización del mundo
inicializar_mundo :-
    retractall(wumpus_pos(_,_)),
    retractall(oro_pos(_,_)),
    retractall(pozo_pos(_,_)),
    retractall(agente_pos(_,_)),
    retractall(agente_dir(_)),
    retractall(tiene_flecha(_)),
    retractall(wumpus_vivo(_)),
    retractall(casilla_visitada(_,_)),
    retractall(casilla_segura(_,_)),
    retractall(casilla_peligrosa(_,_)),
    retractall(percepcion_actual(_)),
    retractall(mundo_creado(_)),
    retractall(oro_recogido(_)),
    retractall(juego_terminado(_)),
    
    % Posición inicial del agente
    assert(agente_pos(1,1)),
    assert(agente_dir(norte)),
    assert(tiene_flecha(true)),
    assert(wumpus_vivo(true)),
    assert(casilla_visitada(1,1)),
    assert(casilla_segura(1,1)),
    assert(oro_recogido(false)),
    assert(juego_terminado(false)),
    
    % Generar posiciones aleatorias
    generar_wumpus,
    generar_oro,
    generar_pozos,
    assert(mundo_creado(true)),
    
    % Mostrar estado inicial
    writeln('=== ESTADO INICIAL DEL MUNDO ==='),
    mostrar_estado_mundo,
    writeln('').

% Generación aleatoria de entidades
generar_wumpus :-
    repeat,
    random_between(1, 4, X),
    random_between(1, 4, Y),
    \+ (X = 1, Y = 1), % No en posición inicial del agente
    assert(wumpus_pos(X, Y)),
    !.

generar_oro :-
    repeat,
    random_between(1, 4, X),
    random_between(1, 4, Y),
    \+ (X = 1, Y = 1), % No en posición inicial
    \+ wumpus_pos(X, Y), % No en posición del wumpus
    assert(oro_pos(X, Y)),
    !.
% Generación de pozos: exactamente 20% del mapa (3 pozos en 4x4)
generar_pozos :-
    % Calcular número de pozos: 20% de las casillas disponibles
    calcular_casillas_disponibles(CasillasDisponibles),
    NumPozos is round(CasillasDisponibles * 0.2),
    writeln('📊 Generando pozos...'),
    format('   Casillas disponibles: ~w~n', [CasillasDisponibles]),
    format('   Pozos a generar (20%): ~w~n', [NumPozos]),
    generar_pozos_exactos(NumPozos).

% Calcular casillas disponibles (excluyendo agente, wumpus y oro)
calcular_casillas_disponibles(Disponibles) :-
    TotalCasillas = 16, % 4x4 = 16 casillas
    CasillasOcupadas = 3, % agente(1,1) + wumpus + oro
    Disponibles is TotalCasillas - CasillasOcupadas.

% Generar exactamente N pozos
generar_pozos_exactos(0) :- 
    writeln('✅ Generación de pozos completada.'), !.

generar_pozos_exactos(N) :-
    N > 0,
    colocar_pozo_aleatorio_unico,
    N1 is N - 1,
    generar_pozos_exactos(N1).

% Colocar un pozo en posición única y válida
colocar_pozo_aleatorio_unico :-
    repeat,
    random_between(1, 4, X),
    random_between(1, 4, Y),
    % Verificar que la posición sea válida y única
    es_posicion_valida_para_pozo(X, Y),
    \+ pozo_pos(X, Y), % No debe haber ya un pozo aquí
    assert(pozo_pos(X, Y)),
    format('   🕳️  Pozo colocado en (~w, ~w)~n', [X, Y]),
    !.

% Verificar si una posición es válida para colocar un pozo
es_posicion_valida_para_pozo(X, Y) :-
    \+ (X = 1, Y = 1),    % No en posición inicial del agente
    \+ wumpus_pos(X, Y),  % No donde está el wumpus
    \+ oro_pos(X, Y).     % No donde está el oro

% Función auxiliar para contar pozos generados (útil para debug)
contar_pozos(Cantidad) :-
    findall(pozo_pos(X, Y), pozo_pos(X, Y), ListaPozos),
    length(ListaPozos, Cantidad).

% Percepciones del agente
percibir :-
    retractall(percepcion_actual(_)),
    agente_pos(X, Y),
    
    % Verificar brisa (pozos adyacentes)
    (hay_pozo_adyacente(X, Y) -> assert(percepcion_actual(brisa)) ; true),
    
    % Verificar hedor (wumpus adyacente)
    (wumpus_vivo(true), hay_wumpus_adyacente(X, Y) -> assert(percepcion_actual(hedor)) ; true),
    
    % Verificar brillo (oro en la misma casilla)
    (oro_pos(X, Y), oro_recogido(false) -> assert(percepcion_actual(brillo)) ; true).

hay_pozo_adyacente(X, Y) :-
    X1 is X - 1, pozo_pos(X1, Y) ; % Oeste
    X1 is X + 1, pozo_pos(X1, Y) ; % Este
    Y1 is Y - 1, pozo_pos(X, Y1) ; % Sur
    Y1 is Y + 1, pozo_pos(X, Y1).  % Norte

hay_wumpus_adyacente(X, Y) :-
    wumpus_pos(WX, WY),
    wumpus_vivo(true),
    (abs(X - WX) =:= 1, Y =:= WY ;
     abs(Y - WY) =:= 1, X =:= WX).

% Movimientos del agente
mover_adelante :-
    \+ juego_terminado(true),
    agente_pos(X, Y),
    agente_dir(Dir),
    nueva_posicion(X, Y, Dir, NX, NY),
    (posicion_valida(NX, NY) ->
        (pozo_pos(NX, NY) ->
            writeln('CAISTE EN UN POZO! JUEGO TERMINADO'),
            retract(juego_terminado(false)),
            assert(juego_terminado(true))
        ; (wumpus_pos(NX, NY), wumpus_vivo(true)) ->
            writeln('EL WUMPUS TE COMIO! JUEGO TERMINADO'),
            retract(juego_terminado(false)),
            assert(juego_terminado(true))
        ;   retract(agente_pos(X, Y)),
            assert(agente_pos(NX, NY)),
            assert(casilla_visitada(NX, NY)),
            writeln('Movimiento: Adelante'),
            format('Nueva posicion: (~w, ~w)~n', [NX, NY])
        )
    ;   writeln('Movimiento bloqueado: Pared')
    ).

nueva_posicion(X, Y, norte, X, Y1) :- Y1 is Y + 1.
nueva_posicion(X, Y, sur, X, Y1) :- Y1 is Y - 1.
nueva_posicion(X, Y, este, X1, Y) :- X1 is X + 1.
nueva_posicion(X, Y, oeste, X1, Y) :- X1 is X - 1.

posicion_valida(X, Y) :-
    X >= 1, X =< 4, Y >= 1, Y =< 4.

girar_izquierda :-
    \+ juego_terminado(true),
    retract(agente_dir(DirActual)),
    nueva_direccion_izq(DirActual, NuevaDir),
    assert(agente_dir(NuevaDir)),
    format('Girando a la izquierda: ~w~n', [NuevaDir]).

nueva_direccion_izq(norte, oeste).
nueva_direccion_izq(oeste, sur).
nueva_direccion_izq(sur, este).
nueva_direccion_izq(este, norte).

girar_derecha :-
    \+ juego_terminado(true),
    retract(agente_dir(DirActual)),
    nueva_direccion_der(DirActual, NuevaDir),
    assert(agente_dir(NuevaDir)),
    format('Girando a la derecha: ~w~n', [NuevaDir]).

nueva_direccion_der(norte, este).
nueva_direccion_der(este, sur).
nueva_direccion_der(sur, oeste).
nueva_direccion_der(oeste, norte).

disparar_flecha :-
    \+ juego_terminado(true),
    (tiene_flecha(true) ->
        retract(tiene_flecha(true)),
        assert(tiene_flecha(false)),
        agente_pos(X, Y),
        agente_dir(Dir),
        disparar_en_direccion(X, Y, Dir),
        writeln('Disparando flecha...')
    ;   writeln('No tienes flecha')
    ).

disparar_en_direccion(X, Y, Dir) :-
    nueva_posicion(X, Y, Dir, TX, TY),
    (posicion_valida(TX, TY) ->
        (wumpus_pos(TX, TY), wumpus_vivo(true) ->
            retract(wumpus_vivo(true)),
            assert(wumpus_vivo(false)),
            assert(percepcion_actual(grito)),
            writeln('GRITO! Wumpus eliminado')
        ;   disparar_en_direccion(TX, TY, Dir)
        )
    ;   writeln('Flecha perdida contra la pared')
    ).

recoger_oro :-
    \+ juego_terminado(true),
    agente_pos(X, Y),
    (oro_pos(X, Y), oro_recogido(false) ->
        retract(oro_recogido(false)),
        assert(oro_recogido(true)),
        writeln('ORO RECOGIDO! GANASTE!')
    ;   writeln('No hay oro aqui')
    ).

salir_cueva :-
    agente_pos(X, Y),
    ((X = 1, Y = 1, oro_recogido(true)) ->
        writeln('SALISTE CON EL ORO! VICTORIA COMPLETA!')
    ; (X = 1, Y = 1) ->
        writeln('Saliste de la cueva (sin oro)')
    ;   writeln('Debes estar en (1,1) para salir')
    ).
% === INTERFAZ GRÁFICA CORREGIDA ===

crear_ventana :-
    (ventana(_) -> 
        ventana(V), send(V, destroy), retract(ventana(V)) 
    ; true),
    
    new(V, dialog('Mundo de Wumpus - Matriz 4x4')),
    assert(ventana(V)),
    
    % Crear canvas principal para la matriz
    new(C, picture('Mundo', size(520, 520))),
    assert(canvas(C)),
    
    % Inicializar estructura de casillas
    retractall(casillas(_)),
    assert(casillas([])),
    
    % Organizar ventana principal
    send(V, append, C),
    
    % Botones de control
    send(V, append, button(paso, message(@prolog, siguiente_paso))),
    send(V, append, button('recoger oro', message(@prolog, recoger_oro))),
    send(V, append, button('salir cueva', message(@prolog, salir_cueva))),
    send(V, append, button(reiniciar, message(@prolog, reiniciar_juego))),
    
    % Controles manuales
    send(V, append, button('Adelante', message(@prolog, mover_adelante))),
    send(V, append, button('Izquierda', message(@prolog, girar_izquierda))),
    send(V, append, button('Derecha', message(@prolog, girar_derecha))),
    send(V, append, button('Disparar', message(@prolog, disparar_flecha))),
    
    send(V, append, button(info, message(@prolog, mostrar_info_completa))),
    send(V, append, button(salir, message(V, destroy))),
    
    % Mostrar ventana
    send(V, open).

dibujar_mundo :-
    canvas(C),
    send(C, clear),
    dibujar_matriz_4x4(C),
    mostrar_info_texto.

dibujar_matriz_4x4(C) :-
    % Título
    send(C, display, text('MUNDO DE WUMPUS 4x4', center, bold), point(260, 10)),
    
    % Dibujar la matriz 4x4
    forall(between(1, 4, Y),
           forall(between(1, 4, X),
                  dibujar_casilla_mejorada(C, X, Y))).

dibujar_casilla_mejorada(C, X, Y) :-
    % Calcular posición (Y invertido para mostrar correctamente)
    PX is (X - 1) * 120 + 20,
    PY is (5 - Y - 1) * 120 + 40,
    
    % Determinar color según estado
    determinar_color_casilla(X, Y, Color),
    
    % Crear casilla
    send(C, display, box(110, 110), point(PX, PY)),
    send(C, display, new(CasillaFondo, box(110, 110)), point(PX, PY)),
    send(CasillaFondo, colour, Color),
    send(CasillaFondo, fill_pattern, Color),
    
    % Coordenadas
    CoordX is PX + 5,
    CoordY is PY + 10,
    atom_concat('(', X, Temp1),
    atom_concat(Temp1, ',', Temp2),
    atom_concat(Temp2, Y, Temp3),
    atom_concat(Temp3, ')', CoordText),
    send(C, display, text(CoordText, left, small), point(CoordX, CoordY)),
    
    % Contenido principal
    TextoX is PX + 55,
    TextoY is PY + 35,
    obtener_texto_casilla(X, Y, Texto),
    send(C, display, text(Texto, center, normal), point(TextoX, TextoY)),
    
    % Información adicional
    InfoY is PY + 55,
    obtener_info_adicional(X, Y, Info),
    send(C, display, text(Info, center, small), point(TextoX, InfoY)),
    
    % Percepciones si es la casilla del agente
    (agente_pos(X, Y) ->
        PercY is PY + 75,
        obtener_percepciones_texto(Percepciones),
        send(C, display, text(Percepciones, center, small), point(TextoX, PercY))
    ; true).

determinar_color_casilla(X, Y, Color) :-
    (agente_pos(X, Y) -> Color = green
    ; casilla_visitada(X, Y) -> Color = lightblue
    ; Color = lightgray).

obtener_texto_casilla(X, Y, Texto) :-
    findall(Item, item_principal_casilla(X, Y, Item), Items),
    (Items = [] -> Texto = ''
    ; atomic_list_concat(Items, ' ', Texto)).

item_principal_casilla(X, Y, 'AGENTE') :- agente_pos(X, Y).
item_principal_casilla(X, Y, 'WUMPUS') :- wumpus_pos(X, Y), wumpus_vivo(true).
item_principal_casilla(X, Y, 'WUMPUS+') :- wumpus_pos(X, Y), wumpus_vivo(false).
item_principal_casilla(X, Y, 'POZO') :- pozo_pos(X, Y).
item_principal_casilla(X, Y, 'ORO') :- oro_pos(X, Y), oro_recogido(false).

obtener_info_adicional(X, Y, Info) :-
    findall(Item, info_secundaria_casilla(X, Y, Item), Items),
    (Items = [] -> Info = ''
    ; atomic_list_concat(Items, ' ', Info)).

info_secundaria_casilla(X, Y, 'BRISA') :- 
    casilla_visitada(X, Y), hay_pozo_adyacente(X, Y).
info_secundaria_casilla(X, Y, 'HEDOR') :- 
    casilla_visitada(X, Y), hay_wumpus_adyacente(X, Y).
info_secundaria_casilla(X, Y, 'BRILLO') :- 
    agente_pos(X, Y), oro_pos(X, Y), oro_recogido(false).
info_secundaria_casilla(X, Y, '?') :- 
    \+ casilla_visitada(X, Y).

obtener_percepciones_texto(Texto) :-
    findall(P, percepcion_actual(P), Percepciones),
    (Percepciones = [] -> Texto = ''
    ; atomic_list_concat(Percepciones, ' ', Texto)).

mostrar_info_texto :-
    agente_pos(X, Y),
    agente_dir(Dir),
    (tiene_flecha(true) -> Flecha = 'SI' ; Flecha = 'NO'),
    (oro_recogido(true) -> Oro = 'SI' ; Oro = 'NO'),
    format('Agente: (~w,~w) Dir:~w Flecha:~w Oro:~w~n', [X, Y, Dir, Flecha, Oro]).

mostrar_info_completa :-
    writeln('=== INFORMACION COMPLETA DEL MUNDO ==='),
    agente_pos(AX, AY),
    agente_dir(Dir),
    format('Agente: (~w, ~w) mirando ~w~n', [AX, AY, Dir]),
    
    wumpus_pos(WX, WY),
    (wumpus_vivo(true) -> EstadoW = 'VIVO' ; EstadoW = 'MUERTO'),
    format('Wumpus: (~w, ~w) - ~w~n', [WX, WY, EstadoW]),
    
    oro_pos(OX, OY),
    (oro_recogido(true) -> EstadoO = 'RECOGIDO' ; EstadoO = 'EN CUEVA'),
    format('Oro: (~w, ~w) - ~w~n', [OX, OY, EstadoO]),
    
    writeln('Pozos:'),
    forall(pozo_pos(PX, PY), format('  (~w, ~w)~n', [PX, PY])),
    
    writeln('Casillas visitadas:'),
    forall(casilla_visitada(VX, VY), format('  (~w, ~w)~n', [VX, VY])),
    
    writeln('Percepciones actuales:'),
    (percepcion_actual(_) ->
        findall(P, percepcion_actual(P), Percepciones),
        format('  ~w~n', [Percepciones])
    ;   writeln('  Ninguna')
    ),
    
    (juego_terminado(true) ->
        writeln('ESTADO: JUEGO TERMINADO')
    ; oro_recogido(true) ->
        writeln('ESTADO: ORO RECOGIDO - Regresa a (1,1)')
    ;   writeln('ESTADO: Juego en progreso')
    ).

% Lógica del juego paso a paso
siguiente_paso :-
    (juego_terminado(true) ->
        writeln('El juego ya termino. Reinicia para jugar de nuevo.')
    ;   writeln('=== SIGUIENTE PASO ==='),
        percibir,
        mostrar_percepciones,
        mostrar_estado_agente,
        decidir_accion,
        dibujar_mundo,
        writeln('')
    ).

mostrar_percepciones :-
    writeln('Percepciones actuales:'),
    (percepcion_actual(_) ->
        findall(P, percepcion_actual(P), Percepciones),
        format('  ~w~n', [Percepciones])
    ;   writeln('  Ninguna')
    ).

mostrar_estado_agente :-
    agente_pos(X, Y),
    agente_dir(Dir),
    tiene_flecha(Flecha),
    format('Agente en: (~w, ~w), Direccion: ~w, Flecha: ~w~n', [X, Y, Dir, Flecha]).

mostrar_estado_mundo :-
    writeln('Posiciones en el mundo:'),
    agente_pos(AX, AY),
    format('  Agente: (~w, ~w)~n', [AX, AY]),
    wumpus_pos(WX, WY),
    format('  Wumpus: (~w, ~w)~n', [WX, WY]),
    oro_pos(OX, OY),
    format('  Oro: (~w, ~w)~n', [OX, OY]),
    writeln('  Pozos:'),
    forall(pozo_pos(PX, PY), format('    (~w, ~w)~n', [PX, PY])).

% Lógica de decisión mejorada
decidir_accion :-
    (percepcion_actual(brillo) ->
        writeln('Accion: Recoger oro'),
        recoger_oro
    ; percepcion_actual(hedor), tiene_flecha(true) ->
        writeln('Accion: Disparar flecha'),
        disparar_flecha
    ; oro_recogido(true) ->
        writeln('Accion: Regresar a (1,1)'),
        accion_regresar_inicio
    ; accion_explorar
    ).

accion_regresar_inicio :-
    agente_pos(X, Y),
    (X = 1, Y = 1 ->
        writeln('En el inicio. Saliendo de la cueva.'),
        salir_cueva
    ; X > 1 ->
        orientar_y_mover(oeste)
    ; Y > 1 ->
        orientar_y_mover(sur)
    ; orientar_y_mover(este)
    ).

accion_explorar :-
    agente_pos(X, Y),
    agente_dir(Dir),
    nueva_posicion(X, Y, Dir, NX, NY),
    (posicion_valida(NX, NY), \+ casilla_visitada(NX, NY), casilla_parece_segura ->
        writeln('Accion: Explorar casilla nueva'),
        mover_adelante
    ; encontrar_direccion_segura(NuevaDir) ->
        orientar_y_mover(NuevaDir)
    ; random_between(1, 2, R),
      (R = 1 -> girar_izquierda ; girar_derecha)
    ).

casilla_parece_segura :-
    \+ percepcion_actual(brisa),
    \+ percepcion_actual(hedor).

encontrar_direccion_segura(Dir) :-
    agente_pos(X, Y),
    member(Dir, [norte, sur, este, oeste]),
    nueva_posicion(X, Y, Dir, NX, NY),
    posicion_valida(NX, NY),
    \+ casilla_visitada(NX, NY).

orientar_y_mover(DirObjetivo) :-
    agente_dir(DirActual),
    (DirActual = DirObjetivo ->
        mover_adelante
    ; girar_hacia(DirObjetivo)
    ).

girar_hacia(DirObjetivo) :-
    agente_dir(DirActual),
    (necesita_girar_derecha(DirActual, DirObjetivo) ->
        girar_derecha
    ; girar_izquierda
    ).

necesita_girar_derecha(norte, este).
necesita_girar_derecha(este, sur).
necesita_girar_derecha(sur, oeste).
necesita_girar_derecha(oeste, norte).

% Predicados principales
jugar :-
    inicializar_mundo,
    crear_ventana,
    dibujar_mundo.

reiniciar_juego :-
    inicializar_mundo,
    dibujar_mundo.

% Inicialización automática
:- initialization(main).

main :-
    writeln('=== MUNDO DE WUMPUS - AGENTE BASADO EN PERCEPCIONES ==='),
    writeln('Comandos disponibles:'),
    writeln('  jugar.           - Iniciar el juego con interfaz grafica'),
    writeln('  siguiente_paso.  - Ejecutar un paso automatico'),
    writeln('  reiniciar_juego. - Reiniciar el mundo'),
    writeln('  mover_adelante.  - Mover agente adelante'),
    writeln('  girar_izquierda. - Girar a la izquierda'),
    writeln('  girar_derecha.   - Girar a la derecha'),
    writeln('  disparar_flecha. - Disparar flecha'),
    writeln('  recoger_oro.     - Recoger oro si esta presente'),
    writeln('  salir_cueva.     - Salir de la cueva desde (1,1)'),
    writeln('  mostrar_info_completa. - Ver informacion detallada'),
    writeln('').
