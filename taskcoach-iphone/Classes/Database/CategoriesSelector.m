//
//  CategoriesSelector.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "CategoriesSelector.h"
#import "Database.h"
#import "Statement.h"
#import "String+Utils.h"

@implementation CategoriesSelector

- (void)onCategory:(NSDictionary *)dict
{
	[clauses addObject:[NSString stringWithFormat:@"idCategory=%d", [[dict objectForKey:@"id"] intValue]]];
	
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id FROM CurrentCategory WHERE parentId=?"]];
	[req bindInteger:[(NSNumber *)[dict objectForKey:@"id"] intValue] atIndex:1];
	[req execWithTarget:self action:@selector(onCategory:)];
}

- initWithId:(NSInteger)catId
{
	if (self = [super init])
	{
		clauses = [[NSMutableArray alloc] init];

		[self onCategory:[NSDictionary dictionaryWithObject:[NSNumber numberWithInt:catId] forKey:@"id"]];
	}
	
	return self;
}

- (NSString *)clause
{
	return [NSString stringWithFormat:@"(%@)", [@" OR " stringByJoiningStrings:clauses]];
}

@end
