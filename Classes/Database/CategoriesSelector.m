//
//  CategoriesSelector.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "CategoriesSelector.h"
#import "Database.h"
#import "Statement.h"
#import "String+Utils.h"

@implementation CategoriesSelector

- initWithId:(NSInteger)catId
{
	if (self = [super init])
	{
		clauses = [[NSMutableArray alloc] init];

		Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id, taskCoachId FROM Category WHERE id=%d", catId]];
		[req execWithTarget:self action:@selector(onCategory:)];
	}
	
	return self;
}

- (NSString *)clause
{
	return [NSString stringWithFormat:@"(%@)", [@" OR " stringByJoiningStrings:clauses]];
}

- (void)onCategory:(NSDictionary *)dict
{
	[clauses addObject:[NSString stringWithFormat:@"idCategory=%d", [[dict objectForKey:@"id"] intValue]]];
	
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id, taskCoachId FROM Category WHERE parentTaskCoachId=?"]];
	[req bindString:[dict objectForKey:@"taskCoachId"] atIndex:1];
	[req execWithTarget:self action:@selector(onCategory:)];
}

@end
