drop table if exists shows;

create table shows (
    id integer primary key autoincrement,
    link text unique not null,
    title text not null,
    content text not null,
    show_date date not null,
    meta json
);
