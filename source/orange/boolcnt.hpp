/*
    This file is part of Orange.

    Orange is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Orange is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Orange; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Authors: Janez Demsar, Blaz Zupan, 1996--2002
    Contact: janez.demsar@fri.uni-lj.si
*/


#ifndef __BOOLCNT_HPP
#define __BOOLCNT_HPP

#include <vector>

using namespace std;

/* Given number of digits and their limit, this counter starts with 01234...d and then increases
   digits, with rightmost the least important. Digit values are ordered in increasing sequence,
   that is 012469 is valid, while 014269 isn't. If a digit reaches limit, its left neighbour is
   increased and the limit reaching digit is reset to the value of the left +1 */
class ORANGE_API TCounter : public vector<int> {
public:
  int limit;

  TCounter(int nums, int alimit);
  bool reset();
  bool next();
  bool prev();
};


/* A base class for counters with binary digits */
class ORANGE_API TBoolCounters : public vector<unsigned char> {
public:
  TBoolCounters(int bits);
  virtual ~TBoolCounters();

  virtual bool next()=0;
  virtual bool prev()=0;

  virtual int bitsOn();
};

/* A constant counter; next and prev are defined but always return false */
class ORANGE_API TBoolCount_const : public TBoolCounters {
public:
  TBoolCount_const(const int n);
  TBoolCount_const(const vector<unsigned char> &ab);

  virtual bool next();
  virtual bool prev();
};

/* A binary counter which always has exactly aset bits set. It can be used to create all the
    subset of a given set with a constant size */
class ORANGE_API TBoolCount_n : public TBoolCounters {
public:
  TCounter counter;

  TBoolCount_n(int bits, int aset);

  virtual bool next();
  virtual bool prev();
  void synchro();

  virtual int bitsOn();
};

/* An ordinary binary counter */
class ORANGE_API TBoolCount : public TBoolCounters {
public:
  TBoolCount(int abits=0);

  virtual bool next();
  virtual bool prev();

  unsigned char neg(unsigned char &b);
};


class ORANGE_API TLimitsCounter : public vector<int> {
public:
  vector<int> limits;

  TLimitsCounter(const vector<int> &alimits);

  virtual bool reset();
  virtual bool next();
  virtual bool prev();
};

#endif

