%define dominates/2 to specify which relations dominate which other ones
dominates(o,p).
dominates(i,p).
dominates(e,d).
dominates(X,X).  % this is to allow a relation to stay the same; will need a special check to ensure at least one relation changes (the \= k condition in the edge/2 relation below.

%define rel/1 and drel/1 to name the different relations; this allows instantiating the variables at the start of the clue. Could have also done this by using dominates to instantiate and having to versions of dominates.
rel(o).
rel(i).
rel(p).
drel(e).
drel(d).
%edge/2 is the core predicate which computes the edges in the CN; one for going from dominating relations to non dominating and one from going the other way round.  Note that we can only have one kind of transition in any edge as dominating ones will happen before any non dominating ones

edge([X1,Y1,Z1],[X2,Y2,Z2]) :- rel(X1), rel(Y1), drel(Z1), dominates(X1,X2), dominates(Y1,Y2), dominates(Z1,Z2), [X1,Y1,Z1] \= [X2,Y2,Z2], [X1,Y1] \= [i,i], [X2,Y2] \= [i,i].
edge([X1,Y1,Z1],[X2,Y2,Z2]) :- rel(X1), rel(Y1), drel(Z1), dominates(X2,X1), dominates(Y2,Y1), dominates(Z2,Z1), [X1,Y1,Z1] \= [X2,Y2,Z2], [X1,Y1] \=  [i,i], [X2,Y2] \= [i,i].

%predicate to collect all the edges into a list L
alledges(L) :- setof([X,Y], edge(X,Y), L).
%can the print these to a file called rcc22cn by saying  alledges(L), print_pairs_to_file(L,rcc22cn).

% print_pairs_to_file(List, Filename)
% Writes each [X,Y] element of List to Filename in format X>Y.

print_pairs_to_file(List, Filename) :-
    open(Filename, write, Stream),
    write_pairs(Stream, List),
    close(Stream).

% Helper predicate to write each pair in the specified format.
write_pairs(_, []).
write_pairs(Stream, [[X, Y]|Tail]) :-
    format(Stream, '~w > ~w~n', [X, Y]),
    write_pairs(Stream, Tail).
