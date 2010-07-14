//
//  String+Utils.h
//  BookBuddy
//
//  Created by Jérôme Laheurte on 26/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

@interface NSString (Utils)

+ (NSString *)stringFromUTF8Data:(NSData *)data;
+ (NSString *)formatTimeInterval:(NSInteger)seconds;

+ (NSString *)decodeData:(NSData *)data;
- (NSData *)encoded;

// Python's string join-like method
- (NSString *)stringByJoiningStrings:(NSArray *)strings;

@end
