//
//  Database.m
//  TestDB
//
//  Created by Jérôme Laheurte on 12/12/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

#import "Database.h"
#import "Statement.h"

static Database *database = nil;

@implementation Database

+ (Database *)connection
{
	if (!database)
	{
		database = [[Database alloc] init];
	}

	return database;
}

- init
{
	NSString* filename = @"taskcoach.db";
	NSArray *documentPaths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
	NSString *documentsDir = [documentPaths objectAtIndex:0];
	NSString *databasePath = [documentsDir stringByAppendingPathComponent:filename];

	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:databasePath])
	{
		NSString *databasePathFromApp = [[NSBundle mainBundle] pathForResource:@"taskcoach" ofType:@"db"];
		[fileManager copyItemAtPath:databasePathFromApp toPath:databasePath error:nil];
	}
	
	[fileManager release];
	
	if (self = [super initWithFilename:databasePath])
	{
		// Nothing yet
	}

	return self;
}

+ (void)close
{
	[database release];

	database = nil;
}

- (void)dealloc
{
	[super dealloc];
}

@end
