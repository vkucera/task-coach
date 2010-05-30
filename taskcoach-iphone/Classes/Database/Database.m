//
//  Database.m
//  TestDB
//
//  Created by Jérôme Laheurte on 12/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "Database.h"
#import "Statement.h"

static Database *database = nil;

@implementation Database

@synthesize currentFile;
@synthesize cdCurrentFile;

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
		[[self statementWithSQL:@"SELECT id FROM TaskCoachFile WHERE visible"] execWithTarget:self action:@selector(updateCurrentFile:)];
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
	self.currentFile = nil;

	[super dealloc];
}

- (void)updateCurrentFile:(NSDictionary *)dict
{
	self.currentFile = [dict objectForKey:@"id"];
}

- (void)onFileNumber:(NSDictionary *)dict
{
	fileNumber = [[dict objectForKey:@"total"] intValue];
}

- (NSInteger)fileNumber
{
	[[self statementWithSQL:@"SELECT COUNT(*) AS total FROM TaskCoachFile"] execWithTarget:self action:@selector(onFileNumber:)];
	
	return fileNumber;
}

- (void)rollback
{
	[super rollback];
	[currentFile release];
	currentFile = nil;
	[[self statementWithSQL:@"SELECT id FROM TaskCoachFile WHERE visible"] execWithTarget:self action:@selector(updateCurrentFile:)];
}

#pragma mark -
#pragma mark CoreData stuff

- (NSInteger)cdFileCount
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
	NSError *error;
	NSInteger count;
	if ((count = [getManagedObjectContext() countForFetchRequest:request error:&error]) < 0)
	{
		NSLog(@"Could not get file count: %@", [error localizedDescription]);
	}

	return count;
}

@end
