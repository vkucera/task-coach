//
//  Database.h
//  TestDB
//
//  Created by Jérôme Laheurte on 12/12/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SQLite.h"

@interface Database : SQLite
{
}

// This is a Singleton
+ (Database *)connection;
+ (void)close;

@end
